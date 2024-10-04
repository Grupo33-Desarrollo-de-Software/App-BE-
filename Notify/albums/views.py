from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.template import loader
import json
import apiExterna.apiExterna as api


def index(request):
    return HttpResponse("Hello, world. You're at the albums index.")


def getAlbum(request):
    busqueda = ""
    try:
        busqueda = request.GET["album"]
    except:
        pass

    resultados = api.buscarAlbums(busqueda)
    print(resultados)
    template = loader.get_template("albums/buscarAlbum.html")
    context = {"resultados": resultados}
    return HttpResponse(template.render(context, request))
