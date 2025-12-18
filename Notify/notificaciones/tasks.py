from background_task import background
from background_task.models import Task
from .actions import recomendarAlbums, nuevoDeArtista
from usuarios.models import Usuario
from followlists.models import Follow


def _run_task_notificaciones():
    #itera sobre todos los usuarios del sistema, ejecutando las acciones de notifs para ellos
    for u in Usuario.objects.all():
        #solo procesa notificaciones para usuarios que tengan al menos un elemento en la fl
        if Follow.objects.filter(usuario=u).exists():
            #genera recomendaciones de álbumes personalizadas para el usuario
            recomendarAlbums(u)
            #notifica sobre nuevos álbumes de artistas que el usuario sigue
            nuevoDeArtista(u)


@background(schedule=5)
def taskNotificaciones_bg():
    # Ejecuta la lógica principal de notificaciones
    _run_task_notificaciones()
    #se reprograma a sí misma para continuar ejecutándose periódicamente
    taskNotificaciones_bg(schedule=5)


def taskNotificaciones(*args, **kwargs):
    #permite ejecutar la tarea de forma sincrona o asincrona (se usa en el testing)
    #si se pasan argumentos, ejecuta la versión en background (asíncrona)
    if args or kwargs:
        return taskNotificaciones_bg(*args, **kwargs)
    #si no hay argumentos, ejecuta directamente la función síncrona
    return _run_task_notificaciones()
