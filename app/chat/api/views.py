import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatMessage, ChatSession
from chat.services.chat_flow import continue_chat

from .serializers import (
    ChatMessageInputSerializer,
    ChatMessageOutputSerializer,
    ChatSessionInputSerializer,
    ChatSessionOutputSerializer,
)

logger = logging.getLogger(__name__)


class CreateChatMessageView(APIView):

    def handle_chat(self, session: ChatSession, prompt: str) -> ChatMessage:
        return continue_chat(session, prompt)

    def post(self, request, session_id: int):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        serializer = ChatMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prompt = serializer.validated_data["prompt"]
        try:
            # hier chatpbot fragen
            msg: ChatMessage = self.handle_chat(session=session, prompt=prompt)
        except Exception as e:
            logger.error("Chat Message fehlgeschlagen: %s", e)
            return Response(
                {"detail": "Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # erfolgreiche Message wird zurückgegeben
        return Response(
            ChatMessageOutputSerializer(msg).data,
            status=status.HTTP_201_CREATED,
        )


class CreateChatSessionView(APIView):
    """Neue Chatsession anlegen."""

    def post(self, request):
        try:
            serializer = ChatSessionInputSerializer(
                data=request.data,
                # damit haben wir Zugriff auf das Request-Objekt im Serializer:
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            chat_session = serializer.save()

            out_serializer = ChatSessionOutputSerializer(chat_session)
            return Response(
                out_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            logger.warning("Validation fehlgeschlagen: %s", e.detail)
            return Response(
                e.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Unerwarter Fehler: %s", e)
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
