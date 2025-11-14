# chat/management/commands/generate_rag_day.py
"""
Chroma.from_texts(
        texts=chunks,
        embedding=embedding,
        collection_name=collection_name,
        client=client,
        metadatas=metadatas,
        ids=[f"{filename}-{i}" for i in range(len(chunks))],
    )
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from chat.services.chroma_utils import store_chunks
from chat.services.embeddings import OpenAiEmbeddingWrapper
from chat.services.text_splitters import split_text

DATA_DIR: Path = settings.BASE_DIR / "data"

FILES = ["eventim_1.txt", "eventim_2.txt"]


def build_metadatas(file: str, chunks: list[str]) -> list[dict]:
    return [
        {"source": file, "chunk_index": i, "length": len(ch)}
        for i, ch in enumerate(chunks)
    ]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--collection", type=str, help="ChromaDB Collection Name", required=True
        )

    def handle(self, *args, **options):
        """Diese Funktion wird vom Command aufgerufen."""
        collection_name = options["collection"]
        for file in FILES:
            text = Path(DATA_DIR / file).read_text(encoding="utf-8")
            chunks = split_text(text)

            store_chunks(
                chunks,
                file,
                collection_name,
                OpenAiEmbeddingWrapper(),
                metadatas=build_metadatas(file, chunks),
            )
