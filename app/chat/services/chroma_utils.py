# services/chroma_utils.py
from chromadb import PersistentClient, Collection

from django.conf import settings
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

from .embeddings import OpenAiEmbeddingWrapper


def get_client() -> PersistentClient:
    """Gib den aktulllen Client zurück. Altrnative: HttpClient()."""
    return PersistentClient(path=settings.BASE_DIR / "chroma_db")


def get_context_chunks(collection_name: str, prompt: str, n: int = 3) -> list[str]:
    """Hole die drei besten Treffer aus ChromaDB."""
    client = get_client()
    collection: Collection = client.get_collection(name=collection_name)
    embedder = OpenAiEmbeddingWrapper()

    # user Prompt anhand OpenAiEmbeddingWrapper vektorisieren
    query_vector = embedder.embed_query(prompt)

    # die n wichtigsten / ähnlichsten Chunks aus der ChromaDB laden
    result_chunks = collection.query(
        query_embeddings=[query_vector],
        n_results=n,
        # where=filtern
    )
    if not result_chunks["documents"] or not result_chunks["documents"][0]:
        return []
    return result_chunks["documents"][0]


def store_chunks(
    chunks: list[str],
    filename: str,
    collection_name: str,
    embedding: Embeddings,
    metadatas: list[dict],
):
    """Speichere Chunks mit Metadaten und Ids in Chromadb."""
    client = get_client()

    # Jeder Chunk braucht ein Meta-Datadict und eine ID
    Chroma.from_texts(
        texts=chunks,
        embedding=embedding,
        collection_name=collection_name,
        client=client,
        metadatas=metadatas,
        ids=[f"{filename}-{i}" for i in range(len(chunks))],
    )
