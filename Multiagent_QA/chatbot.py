from vector_searcher import QdrantSearcher
from database import SQLpostprocessor
from searching_agent import SearchAgent
from summerization_agent import SummarizationAgent
from parsing_agent import ParsingAgent
from logger_config import logger


class NPChatbot:
    def __init__(self, db, openai_client, qdrant_client, parser_template) -> None:
        self.searcher = QdrantSearcher(qdrant_client= qdrant_client, openai_client= openai_client)
        self.sql_processor = SQLpostprocessor()
        self.agent = SearchAgent(db= db, vector_searcher= self.searcher, sql_postprocessor= self.sql_processor, openai_client= openai_client)
        self.summarizer = SummarizationAgent(client= openai_client)
        self.query_parser = ParsingAgent(db=db, output_template=parser_template,
                                                       openai_client=openai_client)
        self.reference = None

    def chat(self, query, parsing_agent_model, searching_agent_model, summarization_agent_model):
        logger.info(f'input: {query}')
        parsed_query = self.query_parser.parse(query, model=parsing_agent_model)
        logger.info(f'parsed_query: {parsed_query}')

        retrieved_df_list = []
        for _, value in parsed_query.items():
            retrieved_data = self.agent.retrieve_data(value, searching_agent_model)
            retrieved_df_list.append(retrieved_data)

        answer = self.summarizer.llm_summarize(original_question=query, parsed_query=parsed_query,
                                               retrieved_df_list=retrieved_df_list,
                                               model=summarization_agent_model)
        self.reset_conversation()
        self.reference = self.summarizer.provide_reference(retrieved_df_list=retrieved_df_list) 
        return str(answer) + self.reference
    def reset_conversation(self):
        self.summarizer.reset_conversation()

