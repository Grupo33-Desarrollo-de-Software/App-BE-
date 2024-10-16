from django.db import models
from usuarios import models as modelUsuario
from albums import models as modelAlbum

# Create your models here.
class follow(models.Model):
    usuario = models.ForeignKey(modelUsuario.Usuario, on_delete=models.CASCADE)
    album = models.ForeignKey(modelAlbum.Album, on_delete=models.CASCADE)


#reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
# en nuestro caso, reporter = usuario, album