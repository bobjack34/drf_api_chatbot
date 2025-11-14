from django.db import models


class BlobJob(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # Beispiel für Metadaten, die du speichern willst
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("error", "Error"),
        ],
    )

    blob_size = models.IntegerField(null=True, blank=True)
    blob_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name} ({self.status})"
