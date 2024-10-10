from django.db import models
from usuarios import models as modelUsuario

# Create your models here.
class notificacion(models.Model):
    titulo = models.CharField(max_length=100)
    cuerpo = models.CharField(max_length=350)
    usuario = modelUsuario.Usuario
    fecha = models.DateField
    leida = models.BooleanField