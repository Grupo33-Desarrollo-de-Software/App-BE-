from background_task import background
from background_task.models import Task
from .actions import recomendarAlbums, nuevoDeArtista
from usuarios.models import Usuario
from followlists.models import Follow


@background(schedule=5)
def taskNotificaciones():
    for u in Usuario.objects.all():
        if Follow.objects.filter(usuario=u).exists():
            recomendarAlbums(u)
            nuevoDeArtista(u)
            print(f"Se crearon notificaciones de {u.username}")
    
    if not Task.objects.filter(task_name="notificaciones.tasks.taskNotificaciones", locked_at__isnull=True).exists():
        taskNotificaciones(schedule=30)
