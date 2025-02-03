from django.shortcuts import render
from django.http import HttpResponse
from requests import Response
from followlists.models import Follow
from calificaciones.models import Rate
from albums.models import Album
from artistas.models import Artista
from django.template import loader
import apiExterna.apiExterna as api
from datetime import datetime
from django.shortcuts import redirect
from rest_framework import viewsets
from .serializers import AlbumSerializer
from notificaciones.views import crearNotificacion
from urllib.parse import urlparse
from apiExterna.apiExterna import sanitizarURL

from rest_framework.response import Response
from rest_framework.decorators import api_view

import logging
l = logging.getLogger(__name__)



def index(request):
    return HttpResponse("Hello, world. You're at the albums index.")


def getAlbum(request):
    try:
        busqueda = request.GET["album"]
        resultados = api.buscarAlbums(busqueda)
        context = {"resultados": resultados}
    except:
        context = {"resultados": []}
    finally:
        template = loader.get_template("albums/buscarAlbum.html")
        return HttpResponse(template.render(context, request))
    
def getInfo(request, artista, album):
    try:
        albumAux = api.buscarAlbum(sanitizarURL(artista), sanitizarURL(album))
        resultado = api.parsearAlbum2(albumAux)
        context = {"resultado": resultado}
    except:
        context = {"resultado": []}
    finally:
        template = loader.get_template("albums/masinfo.html")
        return HttpResponse(template.render(context, request))

def calificar(request, artista, album):
    usuario = request.user
    
    artistaAux = api.getArtista(artista)
    artistaParseado = api.parsearArtista2(artistaAux)
    artistaObjeto, _ = Artista.objects.get_or_create(
        name = artistaParseado["nombre"],
        image = artistaParseado["foto"],
        listeners = artistaParseado["oyentes"],
        plays = artistaParseado["reproducciones"],
        summary = artistaParseado["resumen"]
    )

    albumAux = api.buscarAlbum(artista, album)
    albumParseado = api.parsearAlbum2(albumAux)
    albumObjeto, _ = Album.objects.get_or_create(
        title = albumParseado["titulo"],
        tags = albumParseado["etiquetas"],
        releaseDate = parsearDuracion(albumParseado),
        length = albumParseado["duracion"],
        cover = albumParseado["foto"],
        defaults={"reproducciones": albumParseado["reproducciones"]},
        autor = artistaObjeto
    )
    
    rate = request.POST["rate"]
    comment = request.POST["comment"]

    rateObject, _ = Rate.objects.get_or_create(
        usuario = usuario,
        album = albumObjeto,
        defaults={"rate": rate, "comment": comment}
    )

    rateObject.comment = comment
    rateObject.rate = rate
    rateObject.save()

    l.info(f"El usuario {usuario.username} calificó el album {album}")
    return redirect(request.META.get('HTTP_REFERER'))

def parsearDuracion(albumParseado):
    if albumParseado.get("releaseDate"):
        return datetime.strptime(albumParseado["releaseDate"],"%d %b %Y")
    return None


@api_view(['GET'])
def buscarAlbums(request, album):
    usuario = request.user
    a = api.buscarAlbums(album)
    if usuario.is_authenticated:
        l.info(f"El usuario {usuario.username} buscó {album}")
    else:
        l.info(f"Un usuario anónimo buscó {album}")

    return Response(a)

def persistirAlbum(artista,album):
    fechaLanzamiento = "01 Jan 0001"
    artistaAux = api.getArtista(artista)
    artistaParseado = api.parsearArtista2(artistaAux)
    artistaObjeto, _ = Artista.objects.get_or_create(
        name = artistaParseado["nombre"],
        image = artistaParseado["foto"],
        listeners = artistaParseado["oyentes"],
        plays = artistaParseado["reproducciones"],
        summary = artistaParseado["resumen"]
    )
    if album["fechaLanzamiento"]:
        fechaLanzamiento = album["fechaLanzamiento"]
    albumObjeto, _ = Album.objects.get_or_create(
        title = album["titulo"],
        tags = album["etiquetas"],
        releaseDate = datetime.strptime(fechaLanzamiento, "%d %b %Y"),
        length = album["duracion"],
        cover = album["foto"],
        defaults={"playcount": album["reproducciones"]},
        autor = artistaObjeto
    )
    l.info(f"El album {album.title} fue agregado a la base de datos.")
    return artistaObjeto, albumObjeto

@api_view(['GET'])
def getInfo(request, artista, album):
    usuario = request.user

    if usuario.is_authenticated:
        l.info(f"El usuario {usuario.username} obtuvo información de {album}")
    else:
        l.info(f"Un usuario anónimo obtuvo información de {album}")

    a = api.buscarAlbum(artista, album)
    persistirAlbum(artista, a)
    return Response(a)

@api_view(['GET'])
def seguir(request, artista, album):
    usuario = request.user
    if usuario == None:
        return Response({ "error": "Login required"})
    a = api.buscarAlbum(artista, album)
    _, album = persistirAlbum(artista, a)
    Follow.objects.get_or_create(usuario=usuario, album=album)
    crearNotificacion(usuario, "Seguido con éxito", f"Has seguido con éxito el album {album.title} de {album.autor}")
    
    l.info(f"el usuario {usuario.username} siguió el album {album.title}")
    return Response({"success": "Followed successfully"})

@api_view(['GET'])
def dejarDeSeguir(request, artista, album):

    usuario = request.user
    if usuario == None:
        return Response({ "error": "Login required"})
    a = api.buscarAlbum(artista, album)
    _, album = persistirAlbum(artista, a)
    f, _ = Follow.objects.get_or_create(usuario=usuario, album=album)
    f.delete()

    l.info(f"el usuario {usuario.username} dejó de seguir el album {album.title}")
    return Response({"success": "Unfollowed successfully"})
