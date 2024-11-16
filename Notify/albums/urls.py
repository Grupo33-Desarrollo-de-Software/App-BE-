from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
# router.register(r'album/<str:albumid>', GetAlbumViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("", views.index, name="index"),
    # path("buscar", views.getAlbum, name="getAlbum"),
    # path("detalle/<str:artista>/<str:album>", views.getInfo, name="detalle"),
    # path("follow/<str:artista>/<str:album>", views.seguir, name="seguir"),
]
