from django.contrib import admin

from .models import Category, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sub_title")  # Felder in übersicht
    list_display_links = ("id", "name")  # anklickbar für Detailseite


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sub_title", "category", "author")
    list_display_links = ("id", "name")
