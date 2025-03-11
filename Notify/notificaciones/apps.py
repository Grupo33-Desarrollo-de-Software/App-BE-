from django.apps import AppConfig
from django.conf import settings

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        from .views import scheduleTaskNotificaciones
        # scheduleTaskNotificaciones()
        return super().ready()
