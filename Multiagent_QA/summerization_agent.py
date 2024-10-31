from openai import OpenAI
from datetime import datetime
from variables import sample_questions
import re
import pandas as pd
from logger_config import logger



class SummarizationAgent:
    def __init__(self, client: OpenAI, sample_questions= sample_questions) -> None:
        self.conversation = []
        self.client = client
        self.sample_questions = sample_questions
    @staticmethod
    def is_list_empty(input):
        for elem in input:
            if not isinstance(elem, list) and not isinstance(elem, type(None)):
                return False
        return True

    def llm_summarize(self, original_question, parsed_query, retrieved_df_list, model):
        system_prompt = ''
        original_question_prompt = ''
        
        answer_for_unrelevant = f'''
        Hello! I'm NANOSafari, your dedicated research assistant specializing in nanoparticle drug delivery systems. What can I help you explore today?


        If you're interested, here are some possible topics for inquiry:

        {self.sample_questions}

        Please, go ahead and ask anything that comes to mind!
'''
        if self.is_list_empty(retrieved_df_list):
            system_prompt = f''' 
            As a specialized assistant in the field of nanoparticle drug delivery, please follow these steps to address the user's input:

            1. Assess the relevance of the user's question to nanoparticle drug delivery.
            2. If the input is a greeting or a general statement, or the input is a specific question but is found to be impractical or unrelated to the field, output the whole 'Answer for unrelevant query'(Do not show 'Answer for unrelevant query: ' in reply, and do not change any words).
            There is no need to detail the evaluation process unless it leads to step 3.
            3. If the query is relevant to the field, answer it.
            Answer for unrelevant query: {answer_for_unrelevant}
            '''
            final_prompt = f'''
            Current Input: {original_question}
            '''
        else:
            retrieved_data_final = pd.concat(retrieved_df_list, ignore_index=True)
            retrieved_data_final.index = retrieved_data_final.index + 1

            reference_num_list = [0]
            for i in range(len(retrieved_df_list)):
                reference_num_list.append(reference_num_list[i] + retrieved_df_list[i].shape[0])

            system_prompt = f'''
            
            You are a nanoparticle drug delivery expert, and you are about to receive: 
            1. Questions from the user
            2. Retrieved data from a database 

            Follow these logic to answer the question:

            ### Logic Steps: follow the logic but do not explicitly write them in the response.\n
            Evaluate: Determine if the user's question is practical or relevant to nanoparticle drug delivery. 
            If it is not, provide the reason and end the conversation. 
            If it is relevant, straightly proceed towards the next step. \n
            Provide Detailed Answer: Answer the user's question in a detailed and specific manner, use deductive reasoning, and go deep in each point and go as many sub points as possible.
            The current date is {datetime.now().strftime('%Y-%m-%d')}.Your expertise is strictly limited to the domain of nanoparticle drug delivery, and your responses should reflect this focus.

            Additional Constraints:
            - Refrain from generating or executing any SQL code or database-related commands.
            - Avoid discussing any technical details about database connections, structures, or queries.
            '''

            original_question_prompt = f'''
            According to the given conditioned attributes and targets, answer the question.
            The original question: {original_question}\n
            '''

            sub_question_prompts = ''.join([
                f'''
                    {i + 1}. {elem_dict['question']}
                    Retrieved information: \n{retrieved_data_final.iloc[reference_num_list[i]: reference_num_list[i+1]].to_string()}\n
                    '''
                for i, elem_dict in enumerate(list(parsed_query.values()))
            ])
            # logger.info(f'reference_num_list: {retrieved_data_final.iloc[reference_num_list[i]: reference_num_list[i+1]].to_string()}')
            if len(retrieved_df_list) > 1:
                sub_question_prompts = 'The sub questions separated from the original question:\n' + sub_question_prompts + '\n'

            format_prompt = '''
            
            Format your response as follows, answer in detail:

            
            Provide a detailed answer to the user's question.

            
            Provide a conclusion that summarize the answer.
            
            '''

            additional_prompt = '''
            Citation Instructions:

                1. Index Mark Usage: For cited information, employ index marks [e.g., [3], [15], etc.] that precisely match the sequence of sources listed in your retrieved data(just in the answer, do not attach anything at the end).

                2. Comprehensive Citation: Ensure that index marks are corresponding, do not just sort from 1. Be extensive, providing as many citations (more than 5) possible as in the answer. 
                
                3. Just cite in the answer, do not attach any section after conclution(e.g., citations, reference) at the end.
            '''

            if 'doi' in retrieved_data_final.columns and not retrieved_data_final['doi'].isnull().all():
                final_prompt = original_question_prompt + sub_question_prompts + format_prompt + additional_prompt
            else:
                final_prompt = original_question_prompt + sub_question_prompts + format_prompt


        self.conversation.extend([
            {'role': 'user', 'content': final_prompt}
        ])
        messages= self.conversation + [{'role': 'system', 'content': system_prompt}]
        res = self.client.chat.completions.create(
            model=model,
            messages= messages,
            temperature=1e-19,
            top_p=0.5
        )
        return res.choices[0].message.content

    def reset_conversation(self):
        self.conversation = []

    @staticmethod
    def generate_reference(article_title, doi):
        base_url = "https://doi.org/"
        doi_url = base_url + doi 
        return f"{article_title}. \n DOI: {doi_url}"

    def provide_reference(self, retrieved_df_list):
        if not retrieved_df_list:
            return pd.DataFrame()
        retrieved_data_df = pd.concat(retrieved_df_list, ignore_index=True)
        if retrieved_data_df.empty or ('doi' not in retrieved_data_df.columns) or ('article_title' not in retrieved_data_df.columns):
            return pd.DataFrame()
          
        retrieved_data_df['reference'] = retrieved_data_df.apply(lambda row: self.generate_reference(row['article_title'], row['doi']), axis=1)
          

        references = retrieved_data_df['reference']
        references.index += 1

        return '\n'.join(references.tolist())