from rest_framework import serializers

from blobs import models


class BlobModelSerializer(serializers.ModelSerializer):
    # zusätzliches Feld, das NICHT im Model existiert
    payload = serializers.CharField(write_only=True)

    class Meta:
        model = models.BlobJob  # z. B. Job, Task, Document...
        fields = [
            "id",
            "name",
            "created_at",
            "payload",  # wird angenommen, aber nicht gespeichert
        ]

    def create(self, validated_data) -> models.BlobJob:
        # payload entfernen, soll nicht gespeichert werden
        validated_data.pop("payload", None)

        # Model-Daten speichern
        instance = super().create(validated_data)

        return instance
