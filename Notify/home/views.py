from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.template import loader
import json
from notificaciones.models import Notificacion
from usuarios.models import Usuario
from django.shortcuts import redirect
from django.contrib.auth import logout
# import apiExterna.apiExterna as api

def index(request):
    if request.user.is_authenticated:
        template = loader.get_template("home/index.html")
        usuario = request.user
        if usuario.is_superuser:
          return redirect("/admin")
        notificaciones = Notificacion.objects.filter(usuario=usuario).filter(leida=False)

        context = {"notificaciones": notificaciones, "usuario": usuario}
        return HttpResponse(template.render(context, request))

def crearNotificacion(request, titulo, cuerpo):
    usuario = request.user
    notificacion = Notificacion.objects.create(
        titulo=titulo, cuerpo=cuerpo, usuario=usuario,
    )
    return redirect("/home/")

def logout_view(request):
    logout(request)
    return redirect("/")

def leerNotificacion(request, notificacionId):
    notificacion = Notificacion.objects.get(id=notificacionId)
    notificacion.leida = True
    notificacion.save()
    
    return redirect("/home/")
