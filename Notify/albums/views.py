from django.shortcuts import render
from django.http import HttpResponse
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista
from django.template import loader
import apiExterna.apiExterna as api
from datetime import datetime
from django.shortcuts import redirect

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
        albumAux = api.buscarAlbum(artista, album)
        resultado = api.parsearAlbum2(albumAux)
        context = {"resultado": resultado}
    except:
        context = {"resultado": []}
    finally:
        template = loader.get_template("albums/masinfo.html")
        return HttpResponse(template.render(context, request))

def seguir(request, artista, album):
        usuario = request.user
        print(usuario)
       
        artistaAux = api.buscarArtista(artista)
        artistaParseado = api.parsearArtista2(artistaAux)
        artista, _ = Artista.get_or_create(
            name = artistaParseado["nombre"],
            image = artistaParseado["foto"],
            listeners = artistaParseado["oyentes"],
            plays = artistaParseado["reproducciones"],
            summary = artistaParseado["resumen"]
        )

        albumAux = api.buscarAlbum(artista, album)
        albumParseado = api.parsearAlbum2(albumAux)
        album, _ = Album.objects.get_or_create(
            title = albumParseado["titulo"],
            tags = albumParseado["tags"],
            releaseDate = parsearDuracion(albumParseado),
            length = albumParseado["duracion"],
            cover = albumParseado["foto"],
            defaults={"playcount": albumParseado["playcount"]},
            autor = artista
        )
        
        #print("esto funciona")
        Follow.objects.get_or_create(
            usuario = usuario,
            album = album
        )

        return redirect(request.META.get('HTTP_REFERER'))

def parsearDuracion(albumParseado):
    if albumParseado.get("releaseDate"):
        return datetime.strptime(albumParseado["releaseDate"],"%d %b %Y")
    return None

