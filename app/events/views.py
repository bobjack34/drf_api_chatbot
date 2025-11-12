import logging

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Event

logger = logging.getLogger(__name__)


@login_required  # ist request.user ein gültiges Userobjekt
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
