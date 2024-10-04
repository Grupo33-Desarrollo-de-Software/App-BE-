from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.template import loader
import json


def index(request):
    return HttpResponse("Hello, world. Estás en artistas papá.")


def getArtista(request):
    auxArtista = ""
    try:
        auxArtista = request.GET["artista"]
    except:
        print("No se especificó un artista")
    r = requests.get(
        f"http://ws.audioscrobbler.com/2.0/?method=artist.search&artist={auxArtista}&api_key=490431c7a4b3aa2e25808893a53d2742&format=json",
        params=request.GET,
    )
    template = loader.get_template("artistas/buscarArtista.html")
    Resultados = json.loads(r.text)
    context = {"Resultados": Resultados}
    return HttpResponse(template.render(context, request))
