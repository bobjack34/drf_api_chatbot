from django.contrib.auth import get_user_model
from django.db import models

from project.mixins import DateMixin

User = get_user_model()


class ChatbotContext(models.Model):
    """Definiert das grundelgende Verhalten des Bots,
    zb. KundenSupport-Bot."""

    name = models.CharField(max_length=100, unique=True)
    system_prompt = models.TextField()
    # collection =

    def __str__(self):
        return self.name


class ChatSession(DateMixin):
    """User Chat Session."""

    class Models(models.TextChoices):
        GPT_5_NANO = "gpt-5-nano"
        GPT_4_1_MINI = "gpt-4.1-mini"

    class Provider(models.TextChoices):
        DUMMY = ("dummy", "Dummybot")
        OPENAI = ("openai", "OPEN AI based Bot")
        OPENAI_RAG = ("openai_rag", "OPEN AI RAG based Bot")

    context = models.ForeignKey(
        ChatbotContext,
        on_delete=models.PROTECT,
    )
    initial_message = models.TextField()
    model = models.CharField(
        max_length=30,
        choices=Models.choices,
        default=Models.GPT_4_1_MINI,
        help_text="GPT Model für die Session",
    )
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        default=Provider.DUMMY,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )

    def __str__(self) -> str:
        return f"Session {self.pk} von ({self.user})"


class ChatMessage(DateMixin):
    """Hier werden die Chat Messages abgelegt."""

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    prompt = models.TextField(help_text="User Nachricht / Prompt")
    response_message = models.TextField(
        null=True,
        blank=True,
    )
    response_json = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.session} {self.prompt[:20]}"
