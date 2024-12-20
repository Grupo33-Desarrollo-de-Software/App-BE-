from django.db import models
from usuarios import models as modelUsuario


# Create your models here.
class Notificacion(models.Model):
    titulo = models.CharField(max_length=100)
    cuerpo = models.CharField(max_length=350)
    usuario = models.ForeignKey(modelUsuario.Usuario, on_delete=models.CASCADE)
    fecha = models.DateField
    leida = models.BooleanField
