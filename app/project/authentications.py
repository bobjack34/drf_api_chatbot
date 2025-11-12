from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

User = get_user_model()


class ProxyHeaderAuthentication(BaseAuthentication):
    """
    DRF-kompatible Authentifizierung über Header.
    Erkennt, wenn die Middleware bereits einen User gesetzt hat.

    DRF prüft Authentifizierungen in der Reihenfolge in einer authentications-Liste.
    Deshalb müssen wir für DRF, dass dieses Authentifizierungsverfahren zur verüfung steht.

    authenticication_classes = [ProxyHeaderAuthentication,]
    """

    def authenticate(self, request):
        # WICHTIG: nicht request.user verwenden (würde _authenticate() triggern)
        # sondern das ursprüngliche Django-Request-Objekt
        django_request = getattr(request, "_request", request)

        # Wenn Middleware schon einen authentifizierten User set hat, direkt übernehmen
        user = getattr(django_request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            print("ProxyHeaderAuthentication: using user from middleware:", user)
            return (user, None)

        # Fallback: falls Middleware nicht aktiv ist (reiner API-Aufruf)
        username = request.META.get("HTTP_X_AUTH_REQUEST_USER")
        email = request.META.get("HTTP_X_AUTH_REQUEST_EMAIL")
        print(f"ProxyHeaderAuthentication fallback: username={username}, email={email}")

        if not username:
            return None

        user, _ = User.objects.get_or_create(
            username=username, defaults={"email": email or ""}
        )
        return (user, None)
