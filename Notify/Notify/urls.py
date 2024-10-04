from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("albums/", include("albums.urls")),
    path("artistas/", include("artistas.urls")),
    path("admin/", admin.site.urls),
]
