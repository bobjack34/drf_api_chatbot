from django.urls import path

from .views import CreateChatSessionView, CreateChatMessageView


urlpatterns = [
    path("start", CreateChatSessionView.as_view(), name="start-session"),
    # http://localhost:8000/api/chat/session/1/chat
    path(
        "session/<int:session_id>/chat",
        CreateChatMessageView.as_view(),
        name="chat-msg",
    ),
]
