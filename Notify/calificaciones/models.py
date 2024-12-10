from django.db import models
from usuarios import models as modelUsuario
from albums import models as modelAlbum

CHOICES = (
    (1, 'malísimo'),
    (2, 'meh'),
    (3, 'maso'),
    (4, 'banco'),
    (5, 'AOTY'),
)

class Rate(models.Model):
    usuario = models.ForeignKey(modelUsuario.Usuario, on_delete=models.CASCADE)
    album = models.ForeignKey(modelAlbum.Album, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=CHOICES)
    comment = models.TextField(null=True)
