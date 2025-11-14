from django.urls import path

from .views import BlobAPIView, BlobModelForwardAPIView

urlpatterns = [
    path("process", BlobAPIView.as_view()),
    path("process_remote", BlobModelForwardAPIView.as_view()),  # zu FastAPI
]
