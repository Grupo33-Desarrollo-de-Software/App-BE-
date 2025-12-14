import datetime
import traceback
from .views import logResponsetime
from .models import APIMonitor
from django.utils import timezone

def logResponsetimeMiddleware(get_response):
    #Middleware antiguo
    def middleware(request):
        tiempoAntes = datetime.datetime.now()

        response = get_response(request)

        tiempoDespues = datetime.datetime.now()
        logResponsetime(tiempoDespues - tiempoAntes, request.method, request.path)

        return response
    return middleware


class APIMonitoringMiddleware:

    #Middleware completo de monitoreo de API que captura:
    #- Detalles de solicitud/respuesta
    #- Tiempos de respuesta
    #- Información de errores
    #- Información del usuario
    #- IDs de solicitud para rastreo

    
    # Omitir monitoreo para ciertas rutas (admin, static, etc.)
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Omitir monitoreo para estas rutas
        self.skip_paths = ['/admin', '/static', '/media', '/favicon.ico']
    
    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)
        
        # Solo monitorear rutas de la API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = timezone.now()
        request_id = None
        error_message = None
        stack_trace = None
        status_code = 500
        
        try:
            # Obtener cuerpo de la solicitud y limitar tamaño
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and len(request.body) < 10000:  # Limitar a 10KB
                        request_body = request.body.decode('utf-8', errors='ignore')
                except:
                    pass
            
            response = self.get_response(request)
            status_code = response.status_code
            
            # Calcular tiempo de respuesta
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convertir a milisegundos
            
            # Obtener usuario si está autenticado
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Crear registro de monitoreo
            monitor = APIMonitor.objects.create(
                method=request.method,
                endpoint=request.path,
                status_code=status_code,
                response_time_ms=response_time,
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],  # Limitar longitud
                request_body=request_body[:5000] if request_body else None,  # Limitar longitud
            )
            request_id = monitor.request_id
            
            # Si es un error, registrar más detalles
            if status_code >= 400:
                self._log_error_details(monitor, response, status_code)
            
            # Agregar ID para rastreo
            response['X-Request-ID'] = str(request_id)
            
            return response
            
        except Exception as e:
            # Capturar detalles de la excepción
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Crear registro de monitoreo con detalles del error
            monitor = APIMonitor.objects.create(
                method=request.method,
                endpoint=request.path,
                status_code=500,
                response_time_ms=response_time,
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                error_message=error_message[:2000],  # Limitar longitud
                stack_trace=stack_trace[:5000],  # Limitar longitud
            )
            request_id = monitor.request_id
            raise
    
    def get_client_ip(self, request):
        #Extraer dirección IP del cliente desde la solicitud
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_error_details(self, monitor, response, status_code):
        #Registrar detalles adicionales
        try:
            # Intentar extraer mensaje de error de la respuesta
            if hasattr(response, 'data') and isinstance(response.data, dict):
                error_msg = response.data.get('error') or response.data.get('detail') or str(response.data)
                if error_msg and len(error_msg) < 2000:
                    monitor.error_message = str(error_msg)
                    monitor.save(update_fields=['error_message'])
        except:
            pass
