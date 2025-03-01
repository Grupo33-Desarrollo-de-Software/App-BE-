from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

def index(request):
    if request.method == "GET":
        context = {}
        template = loader.get_template("login/index.html")
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
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
