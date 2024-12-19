'''
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("login.urls")),
    path("albums/", include("albums.urls")),
    path("artistas/", include("artistas.urls")),
    path("admin/", admin.site.urls),
    path("home/", include("home.urls")),
    path("calificar/", include("calificaciones.urls")),
]
'''

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from albums import views

router = routers.DefaultRouter()
router.register(r'albums', views.AlbumViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
]