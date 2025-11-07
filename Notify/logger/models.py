from django.db import models
import uuid

class Log(models.Model):
    logtype = models.CharField(max_length=10)
    body = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-datetime']
        indexes = [
            models.Index(fields=['logtype', 'datetime']),
            models.Index(fields=['datetime']),
        ]


class APIMonitor(models.Model):
    """Model to store detailed API request/response monitoring data"""
    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE, etc.
    endpoint = models.CharField(max_length=500)  # Full path
    status_code = models.IntegerField()
    response_time_ms = models.FloatField()  # Response time in milliseconds
    user = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    stack_trace = models.TextField(null=True, blank=True)
    request_body = models.TextField(null=True, blank=True)  # For debugging (be careful with sensitive data)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['method', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.response_time_ms}ms)"
