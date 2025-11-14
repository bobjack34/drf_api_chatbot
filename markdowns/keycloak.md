
# **Django hinter oauth2-proxy (Keycloak) – Integration & Setup**

Dieses Dokument beschreibt, wie Django und Django REST Framework hinter einem
**oauth2-proxy** betrieben werden, der wiederum an **Keycloak** angebunden ist.
Django führt dabei *keine eigene Authentifizierung* mehr aus,
sondern vertraut den vom Proxy gesetzten HTTP-Headern.

Die hier beschriebene Lösung funktioniert für:

* Django Admin
* klassische Django-Views
* DRF API Views
* pytest (korrektes Verhalten: 401 statt 403)
* lokale Tests ohne Proxy (Header manuell setzen)

---

# **1. Architekturübersicht**

```
Browser
  │
  ▼
[ oauth2-proxy ]
  │
  ▼
[   Django / DRF   ]
```

## oauth2-proxy übernimmt:

* Login über Keycloak
* Token-Validierung
* Session-Verwaltung
* Weiterleitung authentifizierter Requests
* Setzen der Header:

```
X-Auth-Request-User
X-Auth-Request-Email
```

## Django übernimmt:

* Benutzer abgleichen/erstellen
* request.user setzen (über Middleware)
* DRF authentifizieren (über Custom Authentication)

---

# **2. Ziele der Integration**

* Single Sign-On über Keycloak
* Kein eigenes Login in Django
* Kein Token-Parsing in Django
* DRF muss denselben User verwenden wie Django
* Konsistente HTTP-Codes (401 statt 403 bei fehlender Auth)
* Testbarkeit per pytest ohne Proxy

---

# **3. Middleware – request.user setzen**

Datei: `project/middlewares.py`

```python
from django.contrib.auth import get_user_model

User = get_user_model()

class ProxyUserMiddleware:
    """
    Setzt request.user anhand von HTTP-Headern, die z. B. von oauth2-proxy
    zur Verfügung gestellt werden.

    Funktioniert für das Standard-Django-Usermodell (username).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        username = request.META.get("HTTP_X_AUTH_REQUEST_USER")
        email = request.META.get("HTTP_X_AUTH_REQUEST_EMAIL")
        print(f"ProxyUserMiddleware: username={username}, email={email}")

        if username:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email or ""},
            )
            request.user = user
            print(f"Proxy user set: {user.username}")

        return self.get_response(request)
```

**Wichtig:** Diese Middleware muss *vor* der Django-`AuthenticationMiddleware`
in der `middlewares`-Liste in den `settings.py` stehen.

---

# **4. DRF Authentication – Header-Auswertung**

Datei: `project/authentication.py`

```python
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

User = get_user_model()

class ProxyHeaderAuthentication(BaseAuthentication):
    """
    DRF-kompatible Authentifizierung anhand von Proxy-Headern.

    - Wenn Proxy-Header vorhanden → Benutzer laden/erstellen
    - Wenn Proxy-Header fehlen → None zurückgeben (DRF versucht nächste Authentifizierung)
    - authenticate_header() sorgt für 401 statt 403
    """

    def authenticate(self, request):
        username = request.META.get("HTTP_X_AUTH_REQUEST_USER")
        email = request.META.get("HTTP_X_AUTH_REQUEST_EMAIL")
        print(f"ProxyHeaderAuthentication: username={username}, email={email}")

        # Keine Header → dieser Authenticator ist nicht zuständig
        if not username:
            return None

        # Benutzer anhand von Headern laden oder anlegen
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email or ""},
        )
        return (user, None)

    def authenticate_header(self, request):
        """
        Wenn authenticate() None liefert, bestimmt der Rückgabewert, ob
        DRF 401 (String) oder 403 (None) sendet.
        """
        return 'Proxy realm="oauth2-proxy"'
```

### Warum wir `authenticate_header()` überschreiben

Ohne diese Methode würde DRF bei fehlender Authentifizierung:

* **403 Forbidden** statt
* **401 Unauthorized**

zurückgeben.

Mit diesem Override:

* ProxyAuth → None
* DRF → fragt `authenticate_header()`
* → gibt `"Proxy"` zurück
* → DRF sendet **401**

Das ist korrekt für APIs und sorgt dafür, dass pytest richtig funktioniert.

---

# **5. Einstellungen**

Datei: `project/settings.py`

```python
MIDDLEWARE = [
    "project.middlewares.ProxyUserMiddleware",  # <– Proxy zuerst
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "project.authentication.ProxyHeaderAuthentication",
        "rest_framework.authentication.TokenAuthentication",   # optional
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

---

# **6. Beispiel-View**

```python
# user/views.py

from rest_framework import generics, permissions
from .serializers import UserSerializer

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
```

---

# **7. Local Testing über VS Code REST Client**

Datei: `api.http`

```http
### Request behind oauth2-proxy behaviour
GET http://127.0.0.1:8000/api/users/about
X-Auth-Request-User: alice
X-Auth-Request-Email: alice@example.com

### Should return 200 OK
```

Ohne Header:

```http
### Unauthorized request (should return 401)
GET http://127.0.0.1:8000/api/users/about
```

---

# **8. pytest-Verhalten**

```python
@pytest.mark.django_db
def test_unauthorized_about(api_client):
    url = reverse("about")
    response = api_client.get(url)
    assert response.status_code == 401
```

→ funktioniert, weil `authenticate_header()` **401 erzwingt**.
