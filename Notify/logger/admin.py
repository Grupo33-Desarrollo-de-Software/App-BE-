from django.contrib import admin
from .models import Log, APIMonitor


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('logtype', 'body', 'datetime')
    list_filter = ('logtype', 'datetime')
    search_fields = ('body',)
    readonly_fields = ('datetime',)
    ordering = ('-datetime',)


@admin.register(APIMonitor)
class APIMonitorAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'method', 'endpoint', 'status_code', 'response_time_ms', 'timestamp', 'user')
    list_filter = ('status_code', 'method', 'timestamp')
    search_fields = ('endpoint', 'request_id', 'user__username', 'ip_address')
    readonly_fields = ('request_id', 'timestamp', 'method', 'endpoint', 'status_code', 'response_time_ms', 
                      'user', 'ip_address', 'user_agent', 'error_message', 'stack_trace', 'request_body')
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Información de la solicitud', {
            'fields': ('request_id', 'timestamp', 'method', 'endpoint', 'status_code')
        }),
        ('Rendimiento', {
            'fields': ('response_time_ms',)
        }),
        ('Información del usuario', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Detalles del error', {
            'fields': ('error_message', 'stack_trace'),
            'classes': ('collapse',)
        }),
        ('Cuerpo de la solicitud', {
            'fields': ('request_body',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  
    # Previene la creación manual, solo lo permite a través del middleware
    
