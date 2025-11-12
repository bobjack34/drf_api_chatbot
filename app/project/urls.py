"""
project/urls.py
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),
    path("api/events/", include("events.api.urls")),
    path("api/users/", include("users.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    x = debug_toolbar_urls()
    urlpatterns += x
