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
        notificaciones = Notificacion.objects.filter(usuario=usuario)
        context = {"notificaciones": notificaciones, "usuario": usuario}
        return HttpResponse(template.render(context, request))

def crearNotificacion(request):
    usuario = Usuario.objects.get(username="maxi")
    notificacion = Notificacion.objects.create(
        titulo="Bienvenido", cuerpo="Holaa amigo, bienvenido a Notify", usuario=usuario
    )
    return redirect("/home/")

def logout_view(request):
    logout(request)
    return redirect("/")
