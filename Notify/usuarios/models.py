from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    #foto = models.ImageField()
    preferenciaNotificacion = models.TextChoices("mismoArtista", "similares")
    #listaSeguimiento = 
