from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.template import loader
import json
import apiExterna.apiExterna as api


def index(request):
    return HttpResponse("Hello, world. Estás en artistas papá.")


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
