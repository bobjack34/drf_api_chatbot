import pytest
from django.urls import reverse
from rest_framework import status

from events.models import Category


@pytest.mark.django_db
def test_create_category(api_client):
    url = reverse("category-list-create")
    payload = {
        "name": "neue Kategorie",
        "sub_title": "Neuer Subtitle",
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
