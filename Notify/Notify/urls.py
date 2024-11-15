from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.urls import re_path

urlpatterns = [
    path("", include("login.urls")),
    re_path(
        r"^albums/buscarAlbum/",
        TemplateView.as_view(template_name="buscarAlbum.html"),
        name="home",
    ),
    # path("albums/", include("albums.urls")),
    path("artistas/", include("artistas.urls")),
    path("admin/", admin.site.urls),
    # path("home/", include("home.urls")),
    re_path(r"^home/", TemplateView.as_view(template_name="home.html"), name="home"),
]
