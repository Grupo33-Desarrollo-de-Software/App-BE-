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
from django.urls import path, include, re_path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from usuarios.views import UserViewSet, UserLogIn


urlpatterns = [
   path('api/v1/', include('albums.urls')),
   path('api/v1/', include('followlists.urls')),
   path(r'admin/', admin.site.urls),
]


# router = DefaultRouter()
# router.register(r'users', UserViewSet)

# urlpatterns = [
#     path(r'admin/', admin.site.urls),
#     path('api/v1/', include(router.urls)),
#     path('api-user-login/', UserLogIn.as_view()),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#     re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)