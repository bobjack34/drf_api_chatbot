# chat_flow.py
from chat.models import ChatMessage, ChatSession
from chat.services.chatbots.base import ChatBot, Message, Role
from chat.services.chatbots.dummy_chatbot import Dummybot
from chat.services.chatbots.openai_chatbot import OpenAIChatbot
from chat.services.chatbots.openai_rag_chatbot import OpenAIRAGChatbot


def get_session_messages(session: ChatSession) -> list[Message]:
    """
    Build a provider-neutral chat history for the given session.

    The sequence always starts with the session's system prompt
    (ChatSession.initial_message), then appends user/assistant pairs
    in chronological order. If an assistant reply is not yet stored,
    only the trailing user message is included.

    Args:
        session: The chat session whose history should be read.

    Returns:
        A chronological list of Message items shaped like
        {"role": "system" | "user" | "assistant", "content": str}.
    """
    msgs: list[Message] = []
    # selektiere alle Messages dieser Session via related_name=messages
    # values gibt uns nur die beiden Spalten prompt, response_message
    qs = session.messages.order_by("created_at").values("prompt", "response_message")
    for m in qs:
        msgs.append({"role": Role.USER, "content": m["prompt"]})
        if m["response_message"]:
            msgs.append({"role": Role.ASSISTANT, "content": m["response_message"]})
    return msgs


def save_message(
    session: ChatSession, prompt: str, message: str, message_dict: dict
) -> ChatMessage:
    msg = ChatMessage.objects.create(
        session=session,
        prompt=prompt,
        response_message=message,
        response_json=message_dict,
    )
    return msg


def send_prompt(bot: ChatBot, prompt: str) -> tuple[str, dict]:
    """Finally talk with bot."""
    return bot.talk(prompt)


def continue_chat(session: ChatSession, prompt: str) -> ChatMessage:
    """
    => wir bauen die Bot-Instanz (Dummybot)
    => send_prompt()
    => dummy->talk() -> OPENAI
    => Rückgabewrt von talk() ist Message, Json-Repsone
    => das Message Objekt speichern (save_message())
    => Message Objekt zurück (return save_message)

    """
    # besser:factory funktion bauen!
    if session.provider == "dummy":
        bot = Dummybot()
    elif session.provider == "openai":
        messages = get_session_messages(session)
        bot = OpenAIChatbot(
            model=session.model,
            initial_message=session.initial_message,
            messages=messages,
        )
    elif session.provider == "openai_rag":
        messages = get_session_messages(session)
        bot = OpenAIRAGChatbot(
            model=session.model,
            initial_message=session.initial_message,
            messages=messages,
            collection_name="customer",  # besser im Kontext-Model hinterlegen
        )

    try:
        message, message_dict = send_prompt(bot, prompt)
    except Exception as e:
        print(e)

    return save_message(session, prompt, message, message_dict)
