# api/views.py
import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Category, Event
from project.authentications import ProxyHeaderAuthentication

from .serializers import (
    CategorySerializer,
    EventInputSerializer,
    EventOutputSerializer,
    SimpleSerializer,
)

logger = logging.getLogger(__name__)


class EventListCreateAPIView(generics.ListCreateAPIView):
    """

    GET api/events/

    Diese View gibt zwei Serializer zurück:
    Beim Create nutzen wir den EventInputSerializer beim Eingang
    und beim Ausgang den EventOutputSerializer
    """

    authentication_classes = [
        ProxyHeaderAuthentication,
        TokenAuthentication,
    ]  # Wie wird authentifiziert?
    permission_classes = [IsAuthenticated]  # Autorisierung

    # siehe readme für mehr Infos!
    # für Foreign-Key-Beziehungen (zb. Events->Category):
    queryset = Event.objects.select_related("category", "author")

    # für Rerverse-Foreign-Key (zb. Category->events):
    # queryset = Event.objects.prefetch_related("category", "author")

    def get_serializer_class(self) -> serializers.Serializer:
        if self.request.method == "POST":
            # wird bei POST aufgerufen (da wir create überschrieben haben,
            # nutzen wird das nicht direkt)
            return EventInputSerializer
        else:
            # wird bei GET aufgerufen
            return EventOutputSerializer

    def create(self, request, *args, **kwargs):
        """Post Anfrage verarbeiten."""
        input_serializer_class = self.get_serializer_class()
        input_serializer = input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Wenn User authentifziert ist, ist in request.user ein gültiges User-Objekt
        # Wir haben uns via Token authentifiziert
        event = input_serializer.save(author=request.user)

        output_serializer = EventOutputSerializer(event)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Eine View für die Aktionen: PUT, PATCH, GET, DELETE.

    PUT api/events/3
    """

    queryset = Event.objects.all()

    def get_serializer_class(self) -> serializers.Serializer:
        if self.request.method in ("PUT", "PATCH"):
            return EventInputSerializer
        else:
            return EventOutputSerializer

    def update(self, request, *args, **kwargs):
        """PUT: alles updated, PATCH: eine Untergmenge updaten."""
        partial = kwargs.pop("partial", False)  # put oder patch?
        instance = self.get_object()

        # Bestehendes Objekt serialisieren
        input_serializer_class = self.get_serializer_class()
        input_serializer = input_serializer_class(
            instance,
            data=request.data,
            partial=partial,
        )
        # Eingehende Daten validieren und speichern
        input_serializer.is_valid(raise_exception=True)
        event = input_serializer.save()

        # Event serialisieren und zurückgeben
        output_serializer = EventOutputSerializer(event)
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class CategoryListCreateApiView(APIView):
    """
    GET api/events/category
    """

    # keine Auth und keine Permissions
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        categories = Category.objects.all()
        # many=True => eine Liste (bzw. Queryset) übergeben
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST api/events/category
        """
        # eingehende Daten serialisieren (POST)
        serializer = CategorySerializer(data=request.data)

        # wenn man in is_valid() keine Exception ausführt, bricht das Programm
        # an der Stelle nicht ab.
        # prüfen ob eingehende Daten valide sind, falls ja, speichere Objekt in DB
        # und return
        if serializer.is_valid():
            # erstellt neues Kategorieobjekt in DB
            category = serializer.save()
            # ausgehende Daten serialisieren (Return from POST)
            out_serializer = CategorySerializer(category)
            return Response(
                out_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        # Serializer Fehler loggen
        logger.error(serializer.errors)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CategoryDetailApiView(APIView):

    def get_object(self, pk: int) -> Category | None:
        """Hole ein Kategorie-Objekt aus der DB."""
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            logger.warning("Fehlerhafte ID: %s", pk)
        return None

    def get(self, request, pk: int):
        """pk ist die ID aus der URL: 42

        GET api/events/category/42
        """
        category = self.get_object(pk=pk)
        if not category:
            return Response(
                {"detail": f"Ojbekt with ID. {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # gefundenes Objekt serialisieren und in der Response zurückgeben (s.data)
        out_serializer = CategorySerializer(category)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class SimpleView(APIView):
    """ein einfaches VIEW-Beispiel mit post-Methode.

    POST: {"value": 3}
    """

    def get(self, request):
        return Response({"message": "Hello from GET"})

    def post(self, request):
        # in request.data befinden sich die POST-Daten
        print(request.data)
        s = SimpleSerializer(data=request.data)

        # wir setzen die Validierungskette in Gang
        s.is_valid(raise_exception=True)

        # an dieser Stelle sind die Eingabedaten gültig
        value = s.validated_data["value"]
        return Response({"double": value * 2})
