import datetime
import traceback
from .views import logResponsetime
from .models import APIMonitor
from django.utils import timezone


class APIMonitoringMiddleware:
    #middleware completo del panel de monitoreo
    #captura: detalles de get/post, tiempo de respuesta, informacion de errores/usuario, id de solicitud de rastreo
    
    def __init__(self, get_response):
        self.get_response = get_response
        #omitimos monitoreo para estas rutas
        self.skip_paths = ['/admin', '/static', '/media', '/favicon.ico']
    
    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)
        
        #solo monitorear rutas de la API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = timezone.now()
        request_id = None
        error_message = None
        stack_trace = None
        status_code = 500
        
        try:
            #obtenemos cuerpo de la solicitud y limitar tamaño
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and len(request.body) < 10000:  #10KB
                        request_body = request.body.decode('utf-8', errors='ignore')
                except:
                    pass
            
            response = self.get_response(request)
            status_code = response.status_code
            
            #calcular tiempo de respuesta
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  #convertir a ms
            deltatime = end_time - start_time  #logResponsetime
            
            #registrar tiempo de respuesta en Log 
            logResponsetime(deltatime, request.method, request.path)
            
            #obtenemos usuario (si está autenticado)
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            #creamos registro de monitoreo
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
            
            #si es un error, registrar más detalles
            if status_code >= 400:
                self._log_error_details(monitor, response, status_code)
            
            #agregamos ID para rastreo
            response['X-Request-ID'] = str(request_id)
            
            return response
            
        except Exception as e:
            #capturamos detalles de la excepción
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            deltatime = end_time - start_time  # Para logResponsetime
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            #registramos tiempo de respuesta en Log
            logResponsetime(deltatime, request.method, request.path)
            
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            #creamos registro de monitoreo con detalles del error
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
        #extraemos dirección IP del cliente desde la solicitud
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_error_details(self, monitor, response, status_code):
        #registramos detalles adicionales
        try:
            #intentamos extraer mensaje de error de la respuesta
            if hasattr(response, 'data') and isinstance(response.data, dict):
                error_msg = response.data.get('error') or response.data.get('detail') or str(response.data)
                if error_msg and len(error_msg) < 2000:
                    monitor.error_message = str(error_msg)
                    monitor.save(update_fields=['error_message'])
        except:
            pass