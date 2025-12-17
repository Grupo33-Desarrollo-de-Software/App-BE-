import random
from apiExterna import apiExterna
from notificaciones.models import Notificacion
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista
from datetime import datetime, timedelta
from notificaciones.strategies import (
    NotificationContext,
    DatabaseNotificationStrategy,
    EmailNotificationStrategy,
)


# Create your views here.


def crearNotificacion(usuario, titulo, cuerpo):
    """
    Crea y envía una notificación al usuario usando las estrategias configuradas.

    Esta función utiliza el patrón Strategy para permitir agregar nuevos métodos
    de notificación sin modificar el código existente.

    Args:
        usuario: Instancia del modelo Usuario
        titulo: Título de la notificación
        cuerpo: Cuerpo/contenido de la notificación
    """
    # Crear el contexto de notificaciones con las estrategias disponibles
    context = NotificationContext()

    # Agregar estrategias: primero BD (siempre se guarda), luego email (si está habilitado)
    context.add_strategy(DatabaseNotificationStrategy())
    context.add_strategy(EmailNotificationStrategy())

    # Enviar la notificación usando todas las estrategias configuradas
    context.send_notification(usuario, titulo, cuerpo)


def recomendarAlbums(usuario):
    from notificaciones.strategies import RecommendationNotificationStrategy

    titulo = ""
    cuerpo = ""

    strategy = RecommendationNotificationStrategy()
    return strategy.send(usuario, titulo, cuerpo)


def nuevoDeArtista(usuario):
    if not usuario.notifGenerales:
        return

    follows = Follow.objects.filter(usuario=usuario.id)
    if not follows.exists():
        return

    albums = []
    for f in follows:
        a = Album.objects.filter(id=f.album.id).first()
        if a:
            albums.append(a)

    if not albums:
        return

    artistas = []
    for a in albums:
        if a and a.autor:
            artista = Artista.objects.filter(id=a.autor.id).first()
            if artista:
                artistas.append(artista)

    if not artistas:
        return

    nuevos = []
    for artista in artistas:
        try:
            top = apiExterna.getTopAlbumsFromArtista(artista.name)
            if top:
                for album in top:
                    try:
                        if album.get("fechaLanzamiento"):
                            fecha = datetime.strptime(
                                album["fechaLanzamiento"], "%d %b %Y"
                            )
                            semanaPasada = datetime.today() - timedelta(days=7)
                            if fecha > semanaPasada:
                                nuevos.append(album)
                    except (ValueError, KeyError) as e:
                        print(f"Error parseando fecha del álbum: {e}")
                        continue
        except Exception as e:
            print(f"Error obteniendo top álbumes para {artista.name}: {e}")
            continue

    if not nuevos:
        return

    titulo = "Deberías chequear los nuevos álbumes de tus artistas favoritos!!!"
    cuerpo = ""
    for n in nuevos:
        cuerpo += f"{n['titulo']} - {n['artista']}<br/>"

    crearNotificacion(usuario, titulo, cuerpo)
