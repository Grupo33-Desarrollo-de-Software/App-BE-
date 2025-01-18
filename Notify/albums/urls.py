from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("detalle/<str:artista>/<str:album>", views.getInfo, name="detalle"),
    path("calificar/<str:artista>/<str:album>", views.calificar, name="calificar"),
    # path("", views.buscarAlbums),
    path("albums/<str:album>", views.buscarAlbums, name="albums"),
    path("album/<str:artista>/<str:album>", views.getInfo, name="info"),
    path("follow/<str:artista>/<str:album>", views.seguir, name="seguir"),
    path("unfollow/<str:artista>/<str:album>", views.dejarDeSeguir, name="dejarDeSeguir"),
]
