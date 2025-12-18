from django.urls import path
from . import views

#se usa en los tests para configurar los usuarios
urlpatterns = [
    path("configurar", views.configurar, name="configurar"),
]
