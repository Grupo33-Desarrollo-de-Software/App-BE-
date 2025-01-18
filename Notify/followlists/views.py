from django.shortcuts import render
from usuarios.models import Usuario
from .models import Follow
from albums.models import Album
from rest_framework.response import Response
from rest_framework.decorators import api_view
from albums.serializers import AlbumSerializer

@api_view(['GET'])
def mostrarFL(request, nombreUsuario):
    userActual = Usuario.objects.filter(username = nombreUsuario).first()
    followsUser = Follow.objects.all().filter(usuario = userActual.id)
    listaAlbumes = []


    for f in followsUser:
        albumAux = Album.objects.filter(id = f.album.id).first()
        s = AlbumSerializer(albumAux)
        listaAlbumes.append(s.data)
    return  Response(listaAlbumes)

