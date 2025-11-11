from rest_framework import serializers

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


class EventOutputSerializer(serializers.ModelSerializer):
    """Serializer für ausgehende Event-Daten."""

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
