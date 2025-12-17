from background_task.models import Task
from .tasks import taskNotificaciones


def scheduleTaskNotificaciones():
    from .tasks import taskNotificaciones_bg
    task_name = "notificaciones.tasks.taskNotificaciones_bg"
    if not Task.objects.filter(task_name=task_name, locked_at__isnull=True).exists():
        taskNotificaciones_bg(schedule=5)
