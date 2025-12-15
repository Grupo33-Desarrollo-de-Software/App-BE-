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
from notificaciones.actions import crearNotificacion
from apiExterna.apiExterna import sanitizarURL
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from logger.views import logAction, logError, logCrud


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
        name=artistaParseado["nombre"],
        image=artistaParseado["foto"],
        summary=artistaParseado["resumen"],
        defaults={
            "listeners": artistaParseado["oyentes"],
            "plays": artistaParseado["reproducciones"],
        },
    )

    albumParseado = api.buscarAlbum(artista, album)
    albumObjeto, _ = Album.objects.get_or_create(
        title=albumParseado["titulo"],
        tags=albumParseado["etiquetas"],
        releaseDate=parsearFecha(albumParseado),
        length=albumParseado["duracion"],
        cover=albumParseado["foto"],
        defaults={"playcount": albumParseado["reproducciones"]},
        autor=artistaObjeto,
    )

    rate = request.POST["rate"]
    comment = request.POST["comment"]

    rateObject, _ = Rate.objects.get_or_create(
        usuario=usuario, album=albumObjeto, defaults={"rate": rate, "comment": comment}
    )

    rateObject.comment = comment
    rateObject.rate = rate
    rateObject.save()

    logAction(f"El usuario {usuario.username} calificó el album {album}")
    return redirect(request.META.get("HTTP_REFERER"))


def parsearFecha(albumParseado):
    if albumParseado.get("releaseDate"):
        return datetime.strptime(albumParseado["releaseDate"], "%d %b %Y")
    return None


@api_view(["GET"])
@permission_classes([AllowAny])
def buscarAlbums(request, album):
    usuario = request.user
    a = api.buscarAlbums(album)
    term = album.split(" ")[0].lower() if album.lower().startswith("test") else album
    if usuario.is_authenticated:
        logAction(f"El usuario {usuario.username} buscó {term}")
    else:
        logAction(f"Un usuario anónimo buscó {term}")

    return Response(a)


def persistirAlbum(artista, album):
    fechaLanzamiento = "01 Jan 0001"
    artistaAux = api.getArtista(artista)
    artistaParseado = api.parsearArtista2(artistaAux)
    artistaObjeto, _ = Artista.objects.get_or_create(
        name=artistaParseado["nombre"],
        image=artistaParseado["foto"],
        summary=artistaParseado["resumen"],
        defaults={
            "listeners": artistaParseado["oyentes"],
            "plays": artistaParseado["reproducciones"],
        },
    )
    if album["fechaLanzamiento"]:
        fechaLanzamiento = album["fechaLanzamiento"]
    albumObjeto, _ = Album.objects.get_or_create(
        title=album["titulo"],
        tags=album["etiquetas"],
        releaseDate=datetime.strptime(fechaLanzamiento, "%d %b %Y"),
        length=album["duracion"],
        cover=album["foto"],
        defaults={"playcount": album["reproducciones"]},
        autor=artistaObjeto,
    )
    logCrud(f"El album {album['titulo']} fue agregado a la base de datos.")
    return artistaObjeto, albumObjeto


@api_view(["GET"])
@permission_classes([AllowAny])
def getInfo(request, artista, album):
    usuario = request.user
    term = album.split(" ")[0].lower() if album.lower().startswith("test") else album

    if usuario.is_authenticated:
        logAction(f"El usuario {usuario.username} obtuvo información de {term}")
    else:
        logAction(f"Un usuario anónimo obtuvo información de {term}")

    a = api.buscarAlbum(artista, album)
    persistirAlbum(artista, a)
    return Response(a)


@api_view(["GET"])
def seguir(request, artista, album):
    usuario = request.user
    if usuario == None:
        logError("un usuario anónimo intentó seguir un album")
        return Response({"error": "Login required"})
    a = api.buscarAlbum(artista, album)
    _, album = persistirAlbum(artista, a)
    Follow.objects.get_or_create(usuario=usuario, album=album)
    crearNotificacion(
        usuario,
        "Seguido con éxito",
        f"Has seguido con éxito el album {album.title} de {album.autor.name}",
    )

    logAction(f"el usuario {usuario.username} siguió el album {album.title}")
    return Response({"success": "Followed successfully"})


@api_view(["GET"])
def dejarDeSeguir(request, artista, album):

    usuario = request.user
    if usuario == None:
        logError("un usuario anónimo intentó dejar de seguir un album")
        return Response({"error": "Login required"})
    a = api.buscarAlbum(artista, album)
    _, album = persistirAlbum(artista, a)
    f, _ = Follow.objects.get_or_create(usuario=usuario, album=album)
    f.delete()

    logAction(f"el usuario {usuario.username} dejó de seguir el album {album.title}")
    return Response({"success": "Unfollowed successfully"})
