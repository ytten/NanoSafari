from openai import OpenAI
import logging
import datetime


current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


def get_openai_embedding(client:OpenAI, txt, model = 'text-embedding-3-large') -> list[float]:
    return client.embeddings.create(input = [txt], model=model).data[0].embedding
