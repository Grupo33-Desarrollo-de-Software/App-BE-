'''
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buscar", views.getAlbum, name="getAlbum"),
    path("detalle/<str:artista>/<str:album>", views.getInfo, name="detalle"),
    path("follow/<str:artista>/<str:album>", views.seguir, name="seguir"),
    path("calificar/<str:artista>/<str:album>", views.calificar, name="calificar"),
]
'''

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from trivia import views

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
]