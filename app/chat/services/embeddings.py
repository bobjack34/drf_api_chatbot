from langchain_core.embeddings import Embeddings
from openai import OpenAI


class OpenAiEmbeddingWrapper(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_batch_openai(texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_batch_openai([text])[0]


def embed_batch_openai(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using OpenAi Embeddings API."""
    client = OpenAI()
    res = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in res.data]
