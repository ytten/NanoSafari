import json
from openai import OpenAI
from datetime import datetime
from variables import vector_elements_list
from record_time import timeit
import pandas as pd
from logger_config import logger

MAX_RELAXATION = 4
MAX_RETRIEVED_PAPER = 20 
SELECT_ALL_SQL = 'SELECT * from papers;'

class SearchAgent:
    def __init__(self, db, vector_searcher, sql_postprocessor, openai_client: OpenAI):
        self.db = db
        self.attributes = []
        self.table_schema = self.db.table_schema
        self.col_type = {}
        self.vector_elements_list = vector_elements_list
        self.vector_searcher = vector_searcher
        self.sql_postprocessor = sql_postprocessor
        self.client = openai_client

    def _generate_attributes_attrs(self, parsed_query):

        
        if 'conditions' and 'target_attributes' in parsed_query:
            column_names = [column[0] for column in self.table_schema]

            for elem in parsed_query['conditions']:
                if elem['attribute'] not in column_names:
                    parsed_query['conditions'].remove(elem)
                else:
                    self.attributes.append(elem['attribute'])

            for elem in parsed_query['target_attributes']:
                if elem['attribute'] not in column_names:
                    parsed_query['target_attributes'].remove(elem)
                else:
                    self.attributes.append(elem['attribute'])

        return parsed_query
    @timeit
    def _retrieve_data_from_mysql(self, sql):
        retrieved_df = self.db.ask_database(sql)
        if retrieved_df.columns.size > 10:
            logger.info('Retrieved.')
            return retrieved_df
        else:
            relaxed = 0
            relaxed_sql_list = self.sql_postprocessor.relax_sql(sql)
            if relaxed_sql_list:
                while retrieved_df.columns.size < 10 and relaxed < MAX_RELAXATION and relaxed < len(relaxed_sql_list):
                    # logger.info(f'Relaxed sql: {relaxed_sql_list[relaxed]}')
                    retrieved_df = self.db.ask_database(relaxed_sql_list[relaxed])
                    relaxed += 1
                if not retrieved_df.columns.size:
                    retrieved_df = self.db.ask_database(SELECT_ALL_SQL)
                    logger.info('No data retrieved, return raw output.')

            return retrieved_df

    def _retrieve_from_llm_using_SQL(self, parsed_query, model='gpt-4o'):
        retrieved_df = pd.DataFrame()
        print(f'In SQL agent, parsed query: {parsed_query}')
        # if not parsed_query:
            
        # if condition or target attributes are not extracted, but the question is relavent
        if not parsed_query['conditions'] and not parsed_query['target_attributes']:
            return self._retrieve_data_from_mysql(SELECT_ALL_SQL)

        parsed_query['conditions'] = [elem for elem in parsed_query['conditions'] if
                                      (elem['attribute'] not in self.vector_elements_list)]
        logger.info(f'parsed_sub_query: {parsed_query}')
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "ask_database",
                    "description": "Use a function to answer user questions about nanoparticle drug delivery papers, the table is called 'nanoparticles'. Input should be the sql.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": f"""
                                        Convert natural language text to SQL obeying the following rules: 
                                        
                                        1. SQL statement named 'query' extracting info to answer the user's question.
                                        2. If and only if the data type is TEXT, use fuzzy searches in summary; Try to match the most unique word and try only to match once
                                        3. If data type is ENUM, using '=' operator to make searches in conditional statements;
                                        4. When it comes to number or year, use range if you can 
                                        5. These attributes are mandatory: doi, article_title, summary, avg_times_cited, {', '.join(self.attributes)}
                                        6. Always sort the result by avg_times_cited descending unless it is specified 
                                        
                                        SQL should be written using this database schema:
                                        {self.table_schema}.
                                        Generate SQL using only the attributes given 
                                        """,
                            }
                        },
                        "required": ["query"],
                    },
                }
            }
        ]

        conversation = [{
            'role': 'user',
            'content': f'''
            Conditioned attributes and targets: {parsed_query}
            Do not answer.
            '''
        }]

        # Step #1: Prompt with content that may result in function call. In this case the model can identify the
        # information requested by the user is potentially available in the database schema passed to the model in
        # Tools description.
        response = self.client.chat.completions.create(
            model=model,
            messages=conversation, # type: ignore
            tools=tools, # type: ignore
            tool_choice="auto",
            temperature=1e-19,
        )

        # Append the message to messages list
        response_message = response.choices[0].message
        # logger.info(response_message)
        # Step 2: determine if the response from the model includes a tool call.
        
        if response_message.tool_calls:
            logger.info('Function triggered')
            for tool_call in response_message.tool_calls:
                tool_function_name = tool_call.function.name
                tool_function_args = json.loads(tool_call.function.arguments)

                tool_query_string = tool_function_args.get('query', None)
                if not tool_query_string:
                    logger.warning("No query found in tool call")
                    continue

                if tool_function_name == 'ask_database':
                    logger.info(f'Before modification: {tool_query_string}')
                    tool_query_string, attrs_to_postprocess, values = self.sql_postprocessor.regex_sort(tool_query_string, self.attributes)
                    tool_query_string = self.sql_postprocessor.sql_replace_with_summary(tool_query_string)

                    if tool_query_string:
                        logger.info(f'After modification: {tool_query_string}')
                        logger.info(f'Attributes to post-process: {attrs_to_postprocess}')

                        tmp_retrieved = self._retrieve_data_from_mysql(tool_query_string)

                        # Validate and manually sort if all values are present
                        if all(values):
                            tmp_retrieved = self.sql_postprocessor.manually_sort(tmp_retrieved, attrs_to_postprocess, values)

                        # Concatenate results and remove duplicates if necessary
                        if retrieved_df.empty:
                            retrieved_df = tmp_retrieved
                        else:
                            retrieved_df = pd.concat([retrieved_df, tmp_retrieved], ignore_index=True).drop_duplicates()
                    else:
                        logger.info('Potential injection attack or no SQL detected')
                        return retrieved_df
                else:
                    logger.warning(f"Error: function '{tool_function_name}' does not exist")

            return retrieved_df
        else:
            # No function triggered; return an empty DataFrame
            logger.info('No function triggered, returning empty DataFrame')
            return retrieved_df


    def _retrieve_dois_or_output(self, parsed_query, model_json2SQL):

        retrieved_df = self._retrieve_from_llm_using_SQL(parsed_query, model_json2SQL)
        # output is a doi list 
        if retrieved_df.columns.size and 'doi' in retrieved_df.columns:
            dois = retrieved_df['doi'].tolist()
            return dois, retrieved_df
        # output is an empty list
        else:
            return [], retrieved_df
    @timeit
    def retrieve_data(self, parsed_query, model_json2SQL):
        # if impractical, then the parsed query would be {}
        filtered_retrieved_df = pd.DataFrame()
        if not parsed_query or not parsed_query['question'] or ('conditions' not in parsed_query) or ('target_attributes' not in parsed_query):
            return filtered_retrieved_df
        parsed_query = self._generate_attributes_attrs(parsed_query)
        dois_from_mysql, retrieved_df = self._retrieve_dois_or_output(parsed_query, model_json2SQL)
        logger.info(f'mysql retrieved data length: {len(retrieved_df)}')


        final_dois = []
        dois_from_vectorDB = []
        question = parsed_query['question']

        logger.info(f'parsed_query question: {question}')
        dois_from_vectorDB = self.vector_searcher.search(question, 'np_drug_delivery')
        
        logger.info(f'vectordb retrieved data length: {len(dois_from_vectorDB)}')
        
        if dois_from_mysql and dois_from_vectorDB:
            v_set = set(dois_from_vectorDB)
            final_dois = [doi for doi in dois_from_mysql if doi in v_set]


        if not dois_from_mysql:
            final_dois = dois_from_vectorDB

        filtered_retrieved_df = pd.DataFrame()
        logger.info(f'doi length: {len(final_dois)}')
        if retrieved_df.columns.size and final_dois:
            filtered_retrieved_df = retrieved_df[retrieved_df['doi'].isin(final_dois)][:MAX_RETRIEVED_PAPER]
        elif retrieved_df.columns.size:
            filtered_retrieved_df = retrieved_df[:MAX_RETRIEVED_PAPER]
        return filtered_retrieved_df

