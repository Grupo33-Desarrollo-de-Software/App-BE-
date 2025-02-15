from django.urls import path
from . import views

urlpatterns = [
    path("configurar", views.configurar, name="configurar"),
]
