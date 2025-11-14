# services/chatbots/dummy_chatbot.py


class Dummybot:
    """Einfacher Bot zum Testen des Chatflows."""

    def __init__(self):
        print("Dummy bot initialisiert")

    def talk(self, prompt: str) -> tuple[str, dict]:
        return prompt.upper(), {"dummy": prompt}
