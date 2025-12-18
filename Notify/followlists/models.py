from django.db import models
from usuarios import models as modelUsuario
from albums import models as modelAlbum

class Follow(models.Model):
    usuario = models.ForeignKey(modelUsuario.Usuario, on_delete=models.CASCADE)
    album = models.ForeignKey(modelAlbum.Album, on_delete=models.CASCADE)