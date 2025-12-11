import random
from apiExterna import apiExterna
from notificaciones.models import Notificacion
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista
from django.core.mail import send_mail
from datetime import datetime, timedelta


# Create your views here.


def crearNotificacion(usuario, titulo, cuerpo):
    if usuario.notifPorMail and usuario.email:
        send_mail(
            titulo,
            cuerpo,
            "notifymusic33@gmail.com",
            [usuario.email],
            fail_silently=False,
        )
        notificacion = Notificacion.objects.create(
            titulo=titulo,
            cuerpo=cuerpo,
            usuario=usuario,
        )


def recomendarAlbums(usuario):
    if not usuario.notifRecomendaciones:
        return

    follows = Follow.objects.filter(usuario=usuario.id)
    albums = []
    for f in follows:
        a = Album.objects.filter(id=f.album.id).first()
        albums.append(a)
    artistas = []
    for a in albums:
        artista = Artista.objects.filter(id=a.autor.id).first()
        artistas.append(artista)

    # TODO: hacer que solamente recomiende artistas no seguidos
    recomendaciones = []
    for artista in artistas:
        r = apiExterna.getAlbumsSimilares(artista.name)
        recomendaciones.extend(r)

    random.seed()
    random.shuffle(recomendaciones)

    try:
        recomendaciones = recomendaciones[:5]
    except:
        pass

    titulo = "Tal vez te gusten los siguientes álbumes 🧐"
    cuerpo = ""
    for r in recomendaciones:
        cuerpo += f"{r["titulo"]} - {r["artista"]}<br/>"

    crearNotificacion(usuario, titulo, cuerpo)


def nuevoDeArtista(usuario):
    if not usuario.notifGenerales:
        return

    follows = Follow.objects.filter(usuario=usuario.id)
    albums = []
    for f in follows:
        a = Album.objects.filter(id=f.album.id).first()
        albums.append(a)
    artistas = []
    for a in albums:
        artista = Artista.objects.filter(id=a.autor.id).first()
        artistas.append(artista)

    nuevos = []
    for artista in artistas:
        top = apiExterna.getTopAlbumsFromArtista(artista.name)
        for album in top:
            if album["fechaLanzamiento"]:
                fecha = datetime.strptime(album["fechaLanzamiento"], "%d %b %Y")
                semanaPasada = datetime.today() - timedelta(days=7)
                if fecha > semanaPasada:
                    nuevos.append(album)

    if not nuevos:
        return

    titulo = "Deberías chequear los nuevos álbumes de tus artistas favoritos!!!"
    cuerpo = ""
    for n in nuevos:
        cuerpo += f"{n["titulo"]} - {n["artista"]}<br/>"

    crearNotificacion(usuario, titulo, cuerpo)
