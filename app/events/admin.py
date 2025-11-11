from django.contrib import admin

from .models import Category, Event, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")  # Felder in übersicht
    list_display_links = ("id", "name")  # anklickbar für Detailseite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sub_title")  # Felder in übersicht
    list_display_links = ("id", "name")  # anklickbar für Detailseite


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sub_title", "category", "author", "tag_list")
    list_display_links = ("id", "name")

    def tag_list(self, obj: Event) -> str:
        """Erstelle kommaseparierten String der Tags."""
        return ", ".join(t.name for t in obj.tags.all())

    def get_queryset(self, request):
        # Zeige nur Events mit nacht an
        # return super().get_queryset(request)
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return request.user.events.all()
