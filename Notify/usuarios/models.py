from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

class Usuario(AbstractUser):
    bio = models.TextField(blank=True)
    foto = models.ImageField(blank=True)

    def __str__(self):
        return self.username
    preferenciaNotificacion = models.TextChoices("mismoArtista", "similares")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)