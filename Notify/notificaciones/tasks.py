from background_task import background
from background_task.models import Task
from .actions import recomendarAlbums, nuevoDeArtista
from usuarios.models import Usuario
from followlists.models import Follow


def _run_task_notificaciones():
    for u in Usuario.objects.all():
        if Follow.objects.filter(usuario=u).exists():
            recomendarAlbums(u)
            nuevoDeArtista(u)

#tenemos el schedule 5 para que se vea en la demo
@background(schedule=5)
def taskNotificaciones_bg():
    _run_task_notificaciones()
    taskNotificaciones_bg(schedule=5)


def taskNotificaciones(*args, **kwargs):
    if args or kwargs:
        return taskNotificaciones_bg(*args, **kwargs)
    return _run_task_notificaciones()
