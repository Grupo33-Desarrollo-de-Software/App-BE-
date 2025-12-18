from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

def index(request):
    #si tenemos un GET: el usuario esta entrando a la pagina para verla, por lo q mostramos el formulario de login
    if request.method == "GET":
        context = {}
        template = loader.get_template("login/index.html")
        return HttpResponse(template.render(context, request))
    #si tenemos un POST: el usuario lleno el formulario
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            #las credenciales son correctas. logueamos y redirigimos a home
            login(request, user)
            return redirect("/home")
        else:
            #las credenciales no son correctas, recargamos el login
            return redirect("")

