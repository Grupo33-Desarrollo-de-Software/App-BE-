from background_task.models import Task
from .tasks import taskNotificaciones


def scheduleTaskNotificaciones():
    if not Task.objects.filter(task_name="notificaciones.tasks.taskNotificaciones", locked_at__isnull=True).exists():
        taskNotificaciones(schedule=5)
