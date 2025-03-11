from django.urls import path
from . import views

urlpatterns = [
    path("newlog", views.logview, name="newlog"),
    path("logs/<str:logtype>", views.getlogs, name="logs")
]
