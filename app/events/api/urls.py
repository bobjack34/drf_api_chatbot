from django.urls import path

from .views import (
    CategoryDetailApiView,
    CategoryListCreateApiView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    SimpleView,
)

urlpatterns = [
    # api/events/simple
    # für klassenbasierte Views immer as_view() aufrufen
    # as_view() erstellt die Einstiegsfunktion dispatch()
    path("", EventListCreateAPIView.as_view(), name="event-list-create"),
    path(
        "<int:pk>",
        EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event-retrieve-update-destroy",
    ),
    path("simple", SimpleView.as_view(), name="simple"),
    path("category", CategoryListCreateApiView.as_view(), name="category-list-create"),
    path(
        "category/<int:pk>",
        CategoryDetailApiView.as_view(),
        name="category-get",
    ),
]
