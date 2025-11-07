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
        ('Request Information', {
            'fields': ('request_id', 'timestamp', 'method', 'endpoint', 'status_code')
        }),
        ('Performance', {
            'fields': ('response_time_ms',)
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Error Details', {
            'fields': ('error_message', 'stack_trace'),
            'classes': ('collapse',)
        }),
        ('Request Body', {
            'fields': ('request_body',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation - only via middleware
