import datetime
import traceback
import sys
import json
from .views import logResponsetime
from .models import APIMonitor
from django.utils import timezone

def logResponsetimeMiddleware(get_response):
    """Legacy middleware - kept for backward compatibility"""
    def middleware(request):
        tiempoAntes = datetime.datetime.now()

        response = get_response(request)

        tiempoDespues = datetime.datetime.now()
        logResponsetime(tiempoDespues - tiempoAntes, request.method, request.path)

        return response
    return middleware


class APIMonitoringMiddleware:
    """
    Comprehensive API monitoring middleware that captures:
    - Request/response details
    - Response times
    - Error information with stack traces
    - User information
    - Request IDs for tracing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Skip monitoring for these paths (admin, static files, etc.)
        self.skip_paths = ['/admin', '/static', '/media', '/favicon.ico']
    
    def __call__(self, request):
        # Skip monitoring for certain paths
        if any(request.path.startswith(path) for path in self.skip_paths):
            return self.get_response(request)
        
        # Only monitor API endpoints
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = timezone.now()
        request_id = None
        error_message = None
        stack_trace = None
        status_code = 500
        
        try:
            # Get request body (limit size to avoid memory issues)
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'body') and len(request.body) < 10000:  # Limit to 10KB
                        request_body = request.body.decode('utf-8', errors='ignore')
                except:
                    pass
            
            # Process request
            response = self.get_response(request)
            status_code = response.status_code
            
            # Calculate response time
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            # Get user if authenticated
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Create monitoring record
            monitor = APIMonitor.objects.create(
                method=request.method,
                endpoint=request.path,
                status_code=status_code,
                response_time_ms=response_time,
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],  # Limit length
                request_body=request_body[:5000] if request_body else None,  # Limit length
            )
            request_id = monitor.request_id
            
            # If error status code, log additional details
            if status_code >= 400:
                self._log_error_details(monitor, response, status_code)
            
            # Add request ID to response headers for tracing
            response['X-Request-ID'] = str(request_id)
            
            return response
            
        except Exception as e:
            # Capture exception details
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            # Get user if authenticated
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Create monitoring record with error details
            monitor = APIMonitor.objects.create(
                method=request.method,
                endpoint=request.path,
                status_code=500,
                response_time_ms=response_time,
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                error_message=error_message[:2000],  # Limit length
                stack_trace=stack_trace[:5000],  # Limit length
            )
            request_id = monitor.request_id
            
            # Re-raise the exception
            raise
    
    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_error_details(self, monitor, response, status_code):
        """Log additional error details for error responses"""
        try:
            # Try to extract error message from response
            if hasattr(response, 'data') and isinstance(response.data, dict):
                error_msg = response.data.get('error') or response.data.get('detail') or str(response.data)
                if error_msg and len(error_msg) < 2000:
                    monitor.error_message = str(error_msg)
                    monitor.save(update_fields=['error_message'])
        except:
            pass
