from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("crearNotificacion", views.crearNotificacion, name="crearNotificacion"),
    path("logout", views.logout_view, name="logout"),
]
