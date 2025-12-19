from django.urls import path
from . import views

#se usa en los tests para configurar los usuarios
urlpatterns = [
    path("configurar", views.configurar, name="configurar"),
]
"""
ejemplo 
{
  "username": "nuevo_nombre",
  "email": "nuevo@email.com",
  "bio": "Mi nueva biografía",
  "notificaciones": {
    "mail": true,
    "recomendaciones": false,
    "generales": true
  }
}
"""