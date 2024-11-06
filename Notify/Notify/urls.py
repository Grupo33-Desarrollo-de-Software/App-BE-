from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("login.urls")),
    path("albums/", include("albums.urls")),
    path("artistas/", include("artistas.urls")),
    path("admin/", admin.site.urls),
    path("home/", include("home.urls")),

]