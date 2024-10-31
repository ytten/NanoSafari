from qdrant_client.http import models as qdrant_models
from utils import get_openai_embedding
from record_time import timeit

class QdrantSearcher:
    def __init__(self, qdrant_client, openai_client) -> None:
        self.qdrant_client = qdrant_client
        self.openai_client = openai_client
    @timeit
    def search(self, query, collection_name, top_k=200):

        query_dense_vector = get_openai_embedding(self.openai_client, query)
        dense_result = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector = query_dense_vector,
            limit=top_k
        )
        dois = [point.payload['doi'] for point in dense_result]
        return dois
    