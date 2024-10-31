from openai import OpenAI
import json
from record_time import timeit
from database import Database
from options import parse_args
from variables import txt2json_output_template
from logger_config import logger


class ParsingAgent:

    def __init__(self, db, openai_client: OpenAI, output_template= txt2json_output_template) -> None:
        self.db = db
        self.schema = db.table_schema
        self.output_template = output_template
        self.client = openai_client
    @timeit
    def parse(self, question, model='gpt-4o-mini-2024-07-18') -> dict:
        logger.info(f'question: {question}')
        messages = [{
            'role': 'user',
            'content': f'''
            Follow these logic to answer the question:
            ### Logic Steps: follow the logic but do not explicitly write them in the response.\n 
            Step 1: Understand the following query.\n
            Step 2: Judge whether the query includes relevant questions towards the field of nanomedicine.\n
            Step 3: If the answer of step 2 is false, return an empty json.\n
            If the answer of step 2 is true, judge whether the query contain multiple question(s).
            Step 4: If the query is a single question, separate the question including subquestion(number 0), conditioned attributes and target attributes according to the given schema.
            Elif the query contains more than one questions, separate the questions individually into subqueries, 
            including subquestion, conditioned attributes and target attributes according to the given schema. Try to 
            give desired value concisely (no more than 1 word, and be very specific). 
            If the desired value is not relevant towards nanomedicine, leave it empty. 
            Labeling the data type according to the given table schema, every 'attribute' in the JSON must exist in the provided schema.\n
            Return a json file whose format should be as follows.\n\n
            Schema: {self.schema}\n\n Query: {question} \n\n Format: {self.output_template}\n\n
            '''
        }]

        model_response = self.client.chat.completions.create(
            response_format={"type": "json_object"},
            model=model,
            messages=messages, # type: ignore
            temperature=1e-19,
        )

        parsed_query = json.loads(str(model_response.choices[0].message.content))
        return parsed_query


