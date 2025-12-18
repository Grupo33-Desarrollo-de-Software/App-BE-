from django.contrib import admin
from django.urls import path, include, re_path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from usuarios.views import UserViewSet, UserLogIn
from albums.views import getAlbum

#generamos el router estandar de REST
router = DefaultRouter()
router.register(r'users', UserViewSet)

#las urls de notify
urlpatterns = [
    path("", include("login.urls")),
    path("home/", include("home.urls")),
    path("buscar", getAlbum, name="getAlbum"),
    path(r'admin/', admin.site.urls),
    path('api/v1/', include('albums.urls')),
    path('api/v1/', include('followlists.urls')),
    path('api/v1/', include('usuarios.urls')),
    path('api/v1/logger/', include('logger.urls')),
    path('api/v1/', include(router.urls)),
    path('api-user-login/', UserLogIn.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #habilita acceso de archivos media en local
