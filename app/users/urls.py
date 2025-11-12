"""
users/urls.py

Der Pfad zu token holt einen Token via obtain_auth_token von der restframework
auth App. Der Endpunkt wird mit POST angesprochen und es muss username und password
übergeben werden. FAlls kein Token existiert, wird ein neuer erstellt.
"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path("token", obtain_auth_token, name="obtain-auth-token"),
]
