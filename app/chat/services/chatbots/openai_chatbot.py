# openai_chot.py
from collections import deque
import logging

from openai import OpenAI

from .base import ChatbotError, Message, Role

logger = logging.getLogger(__name__)


class OpenAIChatbot:
    """Openai chatbot class zum interagieren mit openai APIs."""

    def __init__(self, model: str, initial_message: str, messages: list[Message]):
        self.model = model
        self.initial_message = initial_message
        self.messages = deque(messages, maxlen=3)

        self.client = OpenAI()
        logger.info("OPENAI CHATBOT initialisiert")

    def _create_message(self, role: Role, content: str) -> Message:
        """Baut ein Dict in Form einer Message auf mit Role und content."""
        return {"role": role, "content": content}

    def talk(self, prompt: str) -> tuple[str, dict]:

        adhoc_messages = [
            self._create_message(role=Role.SYSTEM, content=self.initial_message),
            *self.messages,
            self._create_message(role=Role.USER, content=prompt),
        ]

        print("adhoc_messages:", len(adhoc_messages))

        try:
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
            logger.exception("Error in Chat Complleteion: %s", e)
