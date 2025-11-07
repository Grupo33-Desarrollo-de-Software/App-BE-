from django.urls import path
from . import views

urlpatterns = [
    path("configurar", views.configurar, name="configurar"),
    path("register", views.register, name="register"),
]
