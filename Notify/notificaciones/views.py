from background_task.models import Task

def scheduleTaskNotificaciones():
    #programa la tarea periodica de notifs en background 
    from .tasks import taskNotificaciones_bg
    
    #nombre completo de la tarea en el formato que usa django-background-tasks
    task_name = "notificaciones.tasks.taskNotificaciones_bg"
    
    #veririficamos si ya existe una tarea con este nombre que no esté ejecutándose
    #locked_at__isnull=True significa que la tarea no está actualmente en ejecución
    if not Task.objects.filter(task_name=task_name, locked_at__isnull=True).exists():
        #si no existe una tarea pendiente, programa una nueva que se ejecutará cada 5 segundos (para la demo)
        taskNotificaciones_bg(schedule=5)
