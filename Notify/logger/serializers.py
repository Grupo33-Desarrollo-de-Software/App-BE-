from rest_framework import serializers

from .models import Log, APIMonitor

class LogSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="logtype")
    cuerpo = serializers.CharField(source="body")
    fechahora = serializers.CharField(source="datetime")

    class Meta:
        model = Log
        fields = ["tipo", "cuerpo", "fechahora"]


class APIMonitorSerializer(serializers.ModelSerializer):
    """Serializer for detailed API monitoring data"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    timestamp_formatted = serializers.DateTimeField(source='timestamp', read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = APIMonitor
        fields = [
            'request_id',
            'timestamp',
            'timestamp_formatted',
            'method',
            'endpoint',
            'status_code',
            'response_time_ms',
            'user_username',
            'ip_address',
            'user_agent',
            'error_message',
            'stack_trace',
            'request_body',
        ]
        read_only_fields = fields


class MonitoringMetricsSerializer(serializers.Serializer):
    """Serializer for monitoring dashboard metrics"""
    time_range_hours = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    average_response_time_ms = serializers.FloatField()
    error_count = serializers.IntegerField()
    error_rate_percent = serializers.FloatField()
    error_breakdown = serializers.ListField()
    status_distribution = serializers.ListField()
    response_time_stats = serializers.DictField()
    requests_per_hour = serializers.ListField()
    top_endpoints = serializers.ListField()
    recent_errors = APIMonitorSerializer(many=True)
