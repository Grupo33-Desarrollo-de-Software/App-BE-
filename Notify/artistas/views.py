from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import apiExterna.apiExterna as api


def index(request):
    return HttpResponse("Hello, world. Artistas")


def getArtista(request):
    busqueda = ""
    try:
        busqueda = request.GET["artista"]
        resultados = api.buscarArtista(busqueda)
        context = {"resultados": resultados}
    except:
        context = {"resultados": []}
    finally:
        template = loader.get_template("artistas/buscarArtista.html")
        return HttpResponse(template.render(context, request))
