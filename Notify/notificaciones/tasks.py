from background_task import background
from .actions import recomendarAlbums, nuevoDeArtista
from usuarios.models import Usuario
from followlists.models import Follow


def _run_task_notificaciones():
    for u in Usuario.objects.all():
        f = Follow.objects.filter(usuario=u)
        if f:
            recomendarAlbums(u)
            nuevoDeArtista(u)


@background(schedule=5)
def taskNotificaciones_bg():
    _run_task_notificaciones()


def taskNotificaciones(*args, **kwargs):
    # Ejecuta la lógica de notificaciones sin scheduler (tests) o agenda
    # como tarea en segundo plano si se pasan argumentos (ej. repeat).
    if args or kwargs:
        return taskNotificaciones_bg(*args, **kwargs)
    return _run_task_notificaciones()
