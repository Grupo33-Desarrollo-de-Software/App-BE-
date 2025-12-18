from django.apps import AppConfig
from django.conf import settings
import threading


class NotificacionesConfig(AppConfig):
    #clase de configuracion de la app de django de notificaciones
    #se ejecuta automaticamente cuando django inicia la app
    #programa la tarea periodica de notifs al iniciar el server
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        #se llama cuando la app esta lista. programa la tarea de notifs en un thread para evitar problemas de acceso a la db 
        #importamos y ejecutamos scheduleTaskNotificaciones
        def schedule_task():
            from .views import scheduleTaskNotificaciones
            scheduleTaskNotificaciones()
        
        #nos fijamos de que no estemos ejecutando migraciones antes de ejecutar la tarea
        import sys
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
            #creamos un thread daemon (se termina cuando termina el proceso principal) para programar la tarea sin bloquear la inicialización de Django
            threading.Thread(target=schedule_task, daemon=True).start()
        return super().ready()
