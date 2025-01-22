from django.shortcuts import render

from notificaciones.models import Notificacion

# Create your views here.

def crearNotificacion(usuario, titulo, cuerpo):
    notificacion = Notificacion.objects.create(
        titulo=titulo, cuerpo=cuerpo, usuario=usuario,
    )