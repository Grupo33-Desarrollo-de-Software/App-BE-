from django.db import models


class Artista(models.Model):
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=300) #es un charfield ya que refiere al link de la imagen
    listeners = models.PositiveBigIntegerField(null=True)
    plays = models.PositiveBigIntegerField(null=True)
    summary = models.TextField(null=True)