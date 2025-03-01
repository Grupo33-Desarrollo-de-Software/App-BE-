from background_task.models import Task
from .tasks import taskNotificaciones

def scheduleTaskNotificaciones():
    if not Task.objects.filter(task_name="notificaciones.tasks.taskNotificaciones").exists():
        taskNotificaciones(repeat=5)
