from django.db import models
from artistas.models import Artista

class Album(models.Model):
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)
    releaseDate = models.DateField(null=True)
    length = models.IntegerField()  
    cover = models.CharField(max_length=300) #Es un charfield ya que refiere al link de la imagen
    playcount = models.PositiveBigIntegerField(null=True)
    autor = models.ForeignKey(Artista, on_delete=models.CASCADE)

