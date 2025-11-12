from django.contrib.auth import get_user_model

User = get_user_model()


class ProxyUserMiddleware:
    """
    Middleware für Standard-Django-Usermodell (username als Login).
    Setzt request.user anhand der HTTP-Header, die z. B. von oauth2-proxy kommen.

    klassische Variante mit username als login
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        username = request.META.get("HTTP_X_AUTH_REQUEST_USER")
        email = request.META.get("HTTP_X_AUTH_REQUEST_EMAIL")
        print(f"ProxyUserMiddleware: username={username}, email={email}")

        if username:
            user, _ = User.objects.get_or_create(
                username=username, defaults={"email": email or ""}
            )

            request.user = user

        # Anfrage weiterreichen
        response = self.get_response(request)
        return response
