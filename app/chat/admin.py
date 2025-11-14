from django.contrib import admin

from .models import ChatbotContext, ChatSession, ChatMessage


@admin.register(ChatbotContext)
class ChatbotContextAdmin(admin.ModelAdmin):
    pass


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "context", "model", "provider")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "session")
