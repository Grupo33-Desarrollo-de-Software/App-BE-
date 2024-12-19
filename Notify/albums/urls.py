from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    # path("buscar", views.getAlbum, name="getAlbum"),
    # path("detalle/<str:artista>/<str:album>", views.getInfo, name="detalle"),
    # path("follow/<str:artista>/<str:album>", views.seguir, name="seguir"),
    # path("calificar/<str:artista>/<str:album>", views.calificar, name="calificar"),
    # path("", views.buscarAlbums),
    path("albums/<str:album>", views.buscarAlbums, name="albums"),
]
