from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buscar", views.getAlbum, name="getAlbum"),
    path("detalle/<str:mbid>/", views.getInfo, name="detalle"),
]
