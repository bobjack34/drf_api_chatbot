from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from events.models import Category, Event


class EventInputSerializer(serializers.ModelSerializer):
    """Serializer für eingehende Event-Daten."""

    class Meta:
        model = Event
        # fields = "__all__"
        fields = (
            "name",
            "sub_title",
            "category",
            "date",
            "min_group",
        )

    def validate_sub_title(self, value) -> str:
        if len(value) < 5:
            raise ValidationError("Subtitle darf nicht kleiner 5 zeichen sein.")
        return value


class EventOutputSerializer(serializers.ModelSerializer):
    """Serializer für ausgehende Event-Daten."""

    # stellt statt ID die String-Repräsentation der Kategorie da
    category = serializers.StringRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "sub_title",
            "category",
            "date",
            "min_group",
            "author",
        )


class CategorySerializer(serializers.ModelSerializer):
    # beim ModelSerializer (nimmt die Felder aus dem Model),
    # muss das zu serialisierende Modell in der Meta-Class
    # spezifiziert werden
    class Meta:
        model = Category
        # welche Felder sollen serialisiert werden?
        # id ist per default only
        fields = ("id", "name", "sub_title", "description")


class SimpleSerializer(serializers.Serializer):
    """Serializer ohne Model.

    {"value": 3}
    """

    value = serializers.IntegerField()
