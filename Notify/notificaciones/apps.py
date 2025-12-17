from django.apps import AppConfig
from django.conf import settings
import threading

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        # Programar la tarea en un thread separado para evitar warnings
        # sobre acceso a la BD durante la inicialización
        def schedule_task():
            from .views import scheduleTaskNotificaciones
            scheduleTaskNotificaciones()
        
        # Solo programar si no estamos en modo de migraciones
        import sys
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
            threading.Thread(target=schedule_task, daemon=True).start()
        
        return super().ready()
