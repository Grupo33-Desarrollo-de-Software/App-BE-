from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.template import loader
import json


def index(request):
    return HttpResponse("Hello, world. You're at the albums index.")


def getAlbum(request):
    auxAlbum = ""
    try:
        auxAlbum = request.GET["album"]
    except:
        pass
    r = requests.get(
        f"http://ws.audioscrobbler.com/2.0/?method=album.search&album={auxAlbum}&api_key=490431c7a4b3aa2e25808893a53d2742&format=json",
        params=request.GET,
    )
    template = loader.get_template("albums/buscarAlbum.html")
    Resultados = json.loads(r.text)
    context = {"Resultados": Resultados}
    return HttpResponse(template.render(context, request))


def getArtista(request):
    auxArtista = ""
    try:
        auxArtista = request.GET["artista"]
    except:
        print("nashe")
    r = requests.get(
        f"http://ws.audioscrobbler.com/2.0/?method=artist.search&artist={auxArtista}&api_key=490431c7a4b3aa2e25808893a53d2742&format=json",
        params=request.GET,
    )
    template = loader.get_template("albums/buscarArtista.html")
    Resultados = json.loads(r.text)
    context = {"Resultados": Resultados}
    return HttpResponse(template.render(context, request))
