from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from notificaciones.views import recomendarAlbums
from followlists.models import Follow


def index(request):
    if request.method == "GET":
        context = {}
        template = loader.get_template("login/index.html")
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        print(user)
        print(username)
        print(password)
        if user is not None:
            login(request, user)
            f = Follow.objects.filter(usuario = user.id)
            if len(f) > 0:
                recomendarAlbums(user)
            return redirect("/home")
        else:
            return redirect("")
    # No backend authenticated the credentials
    """try:
        busqueda = request.GET["album"]

        context = {"resultados": resultados}
    except:
        context = {"resultados": []}
    finally:
        template = loader.get_template("albums/buscarAlbum.html")
        return HttpResponse(template.render(context, request))"""
