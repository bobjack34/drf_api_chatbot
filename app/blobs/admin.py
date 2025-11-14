from django.contrib import admin

from blobs.models import BlobJob


@admin.register(BlobJob)
class BlobJobAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at", "status"]
