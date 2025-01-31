import random
from django.shortcuts import render

from apiExterna import apiExterna
from notificaciones.models import Notificacion
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista

# Create your views here.

def crearNotificacion(usuario, titulo, cuerpo):
    notificacion = Notificacion.objects.create(
        titulo=titulo, cuerpo=cuerpo, usuario=usuario,
    )

def recomendarAlbums(usuario):
    follows = Follow.objects.filter(usuario=usuario.id)
    albums = []
    for f in follows:
        a = Album.objects.filter(id = f.album.id).first()
        albums.append(a)
    artistas = []
    for a in albums:
        artista = Artista.objects.filter(id = a.autor.id).first()
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
