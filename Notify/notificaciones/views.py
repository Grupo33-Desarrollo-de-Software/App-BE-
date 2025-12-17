from background_task.models import Task
from .tasks import taskNotificaciones


def scheduleTaskNotificaciones():
    """
    Programa la tarea de notificaciones si no existe ya una pendiente.
    """
    from .tasks import taskNotificaciones_bg
    # Buscar por el nombre correcto de la función decorada
    task_name = "notificaciones.tasks.taskNotificaciones_bg"
    if not Task.objects.filter(task_name=task_name, locked_at__isnull=True).exists():
        taskNotificaciones_bg(schedule=5)
