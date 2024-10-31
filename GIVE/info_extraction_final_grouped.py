import re
import csv
import json
import os
from tqdm import tqdm
from openai import OpenAI
from attr_dict import my_prompt_dict, my_attr_dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import textwrap
from options import parse_args
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



class GIVE:
    def __init__(self, client: OpenAI, attr_dict: dict[str, list[str]], temperature, max_retry, prompt_dict = my_prompt_dict):

        self.client = client
        self.attr_dict = attr_dict
        self.prompt_dict = prompt_dict
        self.temperature = temperature
        self.max_retry = max_retry
    def process_csv(self, csv_path: str) -> list[str]:
        """
        Processes the csv file into a list of text.
        """
        text_list = []

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            _ = next(reader) # The first row contains headers
            for row in reader:
                text_list.append(row[1]) # content

        return text_list
    from sklearn.metrics.pairwise import cosine_similarity
    
    def semantic_similarity(self, str1, str2):
        embeddings = self.client.embeddings.create(input=[str1, str2], model='text-embedding-3-small').data
        emb_1, emb_2 = embeddings[0].embedding, embeddings[1].embedding
        
        return cosine_similarity([emb_1], [emb_2]) # type: ignore

    def chat(self, prompt: str, model:str):
        """
        Chats with the OpenAI API
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': "You are a expert in nanoparticle drug delivery."
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content
    
    def chat_json(self, prompt:str, model:str):
        response = self.client.chat.completions.create(
            response_format={ "type": "json_object" },
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': "You are a expert in nanoparticle drug delivery."
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=self.temperature
        )
        return json.loads(str(response.choices[0].message.content))

    def generate_retrieve_paragraph_prompt(self, text_list, group: str) -> str:

        text_str = ""
        row_count = 1
        for text in text_list:
            text_str += f"Row {row_count}: {text}\n"
            row_count += 1

        prompt = f"""
        ### Given article\n
        {text_str}\n

        ### Query\n
        From the given text, find the rows that are somewhat relevant to {group} with properties: {','.join(my_attr_dict[group])}. You should be as inclusive as possible.
        Answer with the row indexes only.
        """
        return prompt

    def generate_retrieve_answer_prompt(self, text_list, group):

        text_str = ""
        row_count = 1
        for text in text_list:
            text_str += f"Row {row_count}: {text}\n"
            row_count += 1
        
        group_prompts = '\n'.join([
            f'''##### properties: {property}\n##### questions: {questions}\n'''
            for property in my_attr_dict[group]
            for questions in ['\n'.join([my_prompt_dict[property]])]
        ])

        first_round_prompt = f"""
        ### Given article
        {text_str}

        ### Instruction
        Given article, answer the questions of the following group.
        ### Group: {group}\n
        {group_prompts}

        ### Format
        Json key should be corresponding property, Json value should be corresponding answer.

        if the answer is not found, answer None
        """
        first_round_prompt = textwrap.dedent(first_round_prompt)

        return first_round_prompt

    def generate_validate_prompt(self, text_list, group):
        """
        Generates first round prompt for groups.
        """

        text_str = '\n'.join(text_list)
        
        group_prompts = '\n'.join([
            f'''##### properties: {property}\n ##### questions: {questions}\n'''
            for property in my_attr_dict[group]
            for questions in ['\n'.join([my_prompt_dict[property]])]
        ])

        first_round_prompt = f"""
        ### Given article paragraphs
        {text_str}

        ### Instruction
        Given article, answer the questions of the following group.
        ### Group: {group}\n
        {group_prompts}

        ### Format
        Json key should be corresponding property, Json value should be corresponding answer.

        if the answer is not found, answer None
        """
        first_round_prompt = textwrap.dedent(first_round_prompt)

        with open('prompt_grouped_validation.txt','w',encoding='utf-8') as f:
            f.write(first_round_prompt)

        return first_round_prompt

    def validate(self, answer: dict, validation: dict, history: list):
        res = {}
        current_inconsistent = False
        history_inconsistent = True  # Assume history inconsistency by default

        for key in answer.keys():
            answer_val = str(answer[key])
            validation_val = str(validation[key])
            
            # Compare current answer and validation
            sim_score = self.semantic_similarity(answer_val, validation_val)

            if sim_score >= 0.8:
                res[key] = answer_val if len(answer_val) >= len(validation_val) else validation_val
            elif answer_val in validation_val or validation_val in answer_val:
                res[key] = validation_val if len(validation_val) >= len(answer_val) else answer_val
            else:
                res[key] = 'None'
                current_inconsistent = True
            
            # Compare with history only if the current round was inconsistent
            if current_inconsistent:
                for past_answer in history:
                    past_val = str(past_answer[key])
                    sim_score_history = self.semantic_similarity(answer_val, past_val)

                    if sim_score_history >= 0.8 or answer_val in past_val or past_val in answer_val:
                        res[key] = answer_val if len(answer_val) >= len(past_val) else past_val
                        history_inconsistent = False
                        break
        
        # Return False if both current and history checks are inconsistent
        return not (current_inconsistent and history_inconsistent), res

    def extract_info(self, csv_path: str, model):

        res_final = {}
        text_list = self.process_csv(csv_path)
        for group in self.attr_dict:
            retry = 0 
            # iterative validation 
            history = []
            while retry < self.max_retry:
                answer_prompt = self.generate_retrieve_answer_prompt(text_list, group)
                paragraph_prompt = self.generate_retrieve_paragraph_prompt(text_list, group)            
                answers = self.chat_json(answer_prompt, model=model)
                history.append(answers)
                paragraphs = self.chat(paragraph_prompt, model=model)
                paragraph_indices = re.findall(pattern=r'\d+', string=str(paragraphs))
                # validate each attr
                shrinked_context = [text_list[int(i)] for i in paragraph_indices]
                validation_prompt = self.generate_validate_prompt(shrinked_context,group)
                validation_answers = self.chat_json(validation_prompt, model)
                valid, res = self.validate(answers, validation_answers, history)
                res_final.update(res)

                if valid:
                    break 
                else: 
                    retry += 1

        return res_final

    def write_result_as_json(self, res, filename, output_dir):
        filename_json = os.path.splitext(filename)[0] + '.json'
        path = os.path.join(output_dir, filename_json)
        with open(path, 'w') as f: 
            json.dump(res, f)

    def extract_info_from_directory(self, input_path: str, model, max_workers: int, output_path: str):
        
        csv_files = [f for f in os.listdir(input_path) if f.endswith(".csv")]
        
        # Define a worker function that handles the processing of a single file
        def process_file(filename):
            try:
                csv_path = os.path.join(input_path, filename)
                output_file_path = output_path + os.path.splitext(filename)[0] + '.json'
                if not os.path.exists(output_file_path):
                    res = self.extract_info(csv_path, model)
                    self.write_result_as_json(res, filename, output_dir=output_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        # Use ThreadPoolExecutor for multithreading
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_file, filename): filename for filename in csv_files}
            # Use tqdm to display progress
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing CSV files"):
                filename = futures[future]
                try:
                    future.result()  # Ensure any exception is raised here
                except Exception as e:
                    print(f"Exception for file {filename}: {e}")


if __name__ == '__main__':
    args = parse_args()
    chat_client = OpenAI(api_key=args.openai_api_key)
    extractor = GIVE(client=chat_client, attr_dict=my_attr_dict, temperature = args.temperature, max_retry=args.max_try)
    extractor.extract_info_from_directory(args.input_path, args.model, args.thread_num, args.output_path)

