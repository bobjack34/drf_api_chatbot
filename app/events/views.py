import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

from .models import Event


logger = logging.getLogger(__name__)


def hello_world(request: HttpRequest) -> HttpResponse:
    """Eine erste View.

    events/hello-world
    """
    print(request.user)
    print(request.method)
    qs = Event.objects.all()
    qs = qs.filter(name__startswith="Ki")

    qs = Event.objects.filter(category__name__icontains="ki")

    # SQL Statement für qs ausgeben
    logger.info("Query:", str(qs.query))

    return HttpResponse(f"Hallo: {",".join(map(str, qs))}")
