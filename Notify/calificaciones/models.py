from django.db import models
from usuarios import models as modelUsuario
from albums import models as modelAlbum

CHOICES = (
    (1, 'Muy malo'),
    (2, 'Malo'),
    (3, 'Bueno'),
    (4, 'Muy bueno'),
    (5, 'AOTY'),
)

class Rate(models.Model):
    usuario = models.ForeignKey(modelUsuario.Usuario, on_delete=models.CASCADE)
    album = models.ForeignKey(modelAlbum.Album, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=CHOICES)
    comment = models.TextField(null=True)
