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
    # Siempre crear la notificación en la base de datos
    notificacion = Notificacion.objects.create(
        titulo=titulo,
        cuerpo=cuerpo,
        usuario=usuario,
    )
    
    # Enviar email solo si el usuario tiene habilitado el envío por mail
    if usuario.notifPorMail and usuario.email:
        send_mail(
            titulo,
            cuerpo,
            "notifymusic33@gmail.com",
            [usuario.email],
            fail_silently=False,
        )


def recomendarAlbums(usuario):
    if not usuario.notifRecomendaciones:
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

        # TODO: hacer que solamente recomiende artistas no seguidos
        recomendaciones = []
        for artista in artistas:
            try:
                r = apiExterna.getAlbumsSimilares(artista.name)
                if r:
                    recomendaciones.extend(r)
            except Exception as e:
                print(f"Error obteniendo álbumes similares para {artista.name}: {e}")
                continue

        if not recomendaciones:
            return

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
                                fecha = datetime.strptime(album["fechaLanzamiento"], "%d %b %Y")
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
            cuerpo += f"{n["titulo"]} - {n["artista"]}<br/>"

        crearNotificacion(usuario, titulo, cuerpo)