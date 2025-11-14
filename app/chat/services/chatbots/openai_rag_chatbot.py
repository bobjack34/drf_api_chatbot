import logging

from chat.services.chroma_utils import get_context_chunks

from .base import ChatbotError, Message, Role
from .openai_chatbot import OpenAIChatbot

logger = logging.getLogger(__name__)


class OpenAIRAGChatbot(OpenAIChatbot):
    def __init__(self, *args, collection_name: str, **kwargs):
        self.collection_name = collection_name
        super().__init__(*args, **kwargs)
        logger.info("RAG Bot wurde initialisiert")

    def talk(self, prompt: str) -> tuple[str, dict]:
        """Rag gesteuerter Antwortprozess."""
        try:
            context_chunks = get_context_chunks(self.collection_name, prompt)
            context_block = "\n---\n".join(context_chunks)

            adhoc_messages = [
                self._create_message(role=Role.SYSTEM, content=self.initial_message),
                # *self.messages, # historische Nachrichten
                self._create_message(role=Role.SYSTEM, content=context_block),
                self._create_message(role=Role.USER, content=prompt),
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=adhoc_messages,
                max_tokens=400,
                temperature=0,  # 0=deterministisch, 10=sehr kreativ
            )

            message: str | None = (
                response.choices[0].message.content if response.choices else None
            )
            return message, response.to_dict()

        except Exception as e:
            logger.exception("Es ist ein Fehler aufgetreten %s", e)
