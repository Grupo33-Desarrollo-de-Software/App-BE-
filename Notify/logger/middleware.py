import datetime
from .views import logResponsetime

def logResponsetimeMiddleware(get_response):
    def middleware(request):
        tiempoAntes = datetime.datetime.now()

        response = get_response(request)

        tiempoDespues = datetime.datetime.now()
        logResponsetime(tiempoDespues - tiempoAntes, request.method, request.path)

        return response
    return middleware
