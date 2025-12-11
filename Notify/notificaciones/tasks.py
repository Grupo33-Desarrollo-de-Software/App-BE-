from background_task import background
from .actions import recomendarAlbums, nuevoDeArtista
from usuarios.models import Usuario
from followlists.models import Follow


@background(schedule=5)
def taskNotificaciones():
    for u in Usuario.objects.all():
        f = Follow.objects.filter(usuario=u)
        if f:
            recomendarAlbums(u)
            nuevoDeArtista(u)
        print(f"se crearon notificaciones de {u.username}")
