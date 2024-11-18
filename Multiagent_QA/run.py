from openai import OpenAI
from qdrant_client import QdrantClient
import os 
from database import Database
from chatbot import NPChatbot
from variables import sample_question, txt2json_output_template
from options import parse_args

def init(args):

    # openai_client = OpenAI(api_key=args.openai_api_key)
    openai_client = OpenAI(api_key=args.openai_api_key)
    qdrant_client = QdrantClient(path=args.vectorDB_path)

    db = Database(
        db_path=args.sqlite_path
        # host=args.mysql_address,
        # user=args.mysql_username,
        # password=args.mysql_password,
        # database=args.mysql_db_name
    )
    chatbot = NPChatbot(db= db,openai_client= openai_client, qdrant_client= qdrant_client, parser_template= txt2json_output_template)
    return chatbot 

if __name__ == '__main__':
    args = parse_args()
    chatbot = init(args)
    answer = chatbot.chat(query=sample_question, parsing_agent_model=args.parsing_agent_model, searching_agent_model=args.searching_agent_model, summarization_agent_model=args.summarization_agent_model)
    
    with open('output.md', 'w') as f:
        f.write(answer) # type: ignore
