# base.py
from enum import StrEnum
from typing import Protocol, TypedDict


class ChatbotError(Exception):
    pass


class Role(StrEnum):
    """Enum representing the role of a the OpenAI API."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(TypedDict):
    """So muss das Message Dictionary aussehen!"""

    role: Role
    content: str


class ChatBot(Protocol):
    def talk(self, prompt: str) -> tuple[dict, str | dict]:
        """Send a prompt to the chatbot and return the response."""
        raise NotImplementedError
