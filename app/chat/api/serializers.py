from rest_framework import serializers

from chat.models import ChatbotContext, ChatMessage, ChatSession


def get_initial_message(session_message: str, context_message: str) -> str:
    """Kombiniere Session-Message mit Kontext-Systemprompt."""
    return "\n".join([context_message, session_message])


class ChatSessionInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatSession
        fields = ["context_id", "model", "initial_message"]

    context_id = serializers.IntegerField(write_only=True)

    def validate_context_id(self, context_id: int) -> int:
        """Prüfen, ob der übergebene Kontext existiert."""
        try:
            ChatbotContext.objects.get(pk=context_id)
            return context_id
        except ChatbotContext.DoesNotExist as e:
            raise serializers.ValidationError("Context wurde nicht gefunden") from e

    def create(self, validated_data: dict) -> ChatSession:
        request = self.context["request"]  # Zugriff auf das Django-Request-Objekt
        ctx = ChatbotContext.objects.get(pk=validated_data.pop("context_id"))

        return ChatSession.objects.create(
            user=request.user,
            context=ctx,
            model=validated_data.get("model"),
            provider=ChatSession.Provider.DUMMY,
            initial_message=get_initial_message(
                session_message=validated_data["initial_message"],
                context_message=ctx.system_prompt,
            ),
        )


class ChatSessionOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatSession
        fields = ["id", "created_at", "model", "initial_message"]


class ChatMessageInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["prompt"]

    def validate_prompt(self, value) -> str:
        if isinstance(value, str) and not value.strip():
            raise serializers.ValidationError("Prompt darf nicht leer sein!")
        return value


class ChatMessageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "session", "prompt", "response_message"]
