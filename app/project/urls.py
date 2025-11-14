"""
project/urls.py
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),
    path("api/events/", include("events.api.urls")),
    path("api/users/", include("users.urls")),  # kein api-Verzeichnis!
    path("api/chat/", include("chat.api.urls")),
    path("api/blobs/", include("blobs.api.urls")),  # api/blobs/process_remote
    path(
        "schema/",
        SpectacularAPIView.as_view(api_version="v2"),
        name="schema",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    x = debug_toolbar_urls()
    urlpatterns += x
