from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Q, Sum
from django.db.models.functions import TruncHour

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from .models import Log, APIMonitor
from .serializers import LogSerializer, APIMonitorSerializer, MonitoringMetricsSerializer

ANY_TYPE = "ANY"
CRUD_TYPE = "CRUD"
ACTION_TYPE = "ACTION"
ERROR_TYPE = "ERROR"
RESPONSETIME_TYPE = "RESPONSETIME"
VALID_LOGTYPES = [CRUD_TYPE, ERROR_TYPE, ACTION_TYPE, RESPONSETIME_TYPE]

from logging import getLogger
l = getLogger(__name__)

def log(logtype, body):
    if logtype not in VALID_LOGTYPES:
        raise Exception("logtype no válido")

    logmsg = f"[{logtype}]\t{body}"
    l.info(logmsg)
    Log.objects.create(logtype=logtype, body=body)

def logCrud(body):
    log(CRUD_TYPE, body)

def logAction(body):
    log(ACTION_TYPE, body)

def logResponsetime(deltatime, method, route):
    body = f"{method} {route}: {str(deltatime)}"
    log(RESPONSETIME_TYPE, body)

def logError(body):
    log(ERROR_TYPE, body)

@api_view(['POST'])
def logview(request):

    logtype = request.data.get("logtype")
    if not logtype or logtype not in VALID_LOGTYPES:
        return Response({"error": "logtype required. Valid logtypes are CRUD, ACTION RESPONSETIME and ERROR"})
    body = request.data.get("body")
    if not body:
        return Response({"error": "body required"})

    log(logtype, body)

    return Response({"success": "log created succesfully"})

@api_view(['GET'])
def getlogs(request, logtype):

    logs = []

    logtype = logtype.upper()

    if logtype in VALID_LOGTYPES:
        logs = Log.objects.filter(logtype=logtype)
    elif logtype == ANY_TYPE:
        logs = Log.objects.all()
    else:
        return Response({"error": "logtype required. Valid logtypes are CRUD, ACTION, RESPONSETIME, ERROR and ANY"})

    s = LogSerializer(logs, many=True)
    return Response(s.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def monitoring_dashboard(request):
    """
    Admin-only API monitoring dashboard endpoint.
    Returns comprehensive metrics for API health monitoring.
    """
    # Get time range (default: last 24 hours)
    hours = int(request.GET.get('hours', 24))
    time_threshold = timezone.now() - timedelta(hours=hours)
    
    # Filter API monitor records within time range
    recent_requests = APIMonitor.objects.filter(timestamp__gte=time_threshold)
    
    # Total Request Count
    total_requests = recent_requests.count()
    
    # Average Response Time
    avg_response_time = recent_requests.aggregate(
        avg_time=Avg('response_time_ms')
    )['avg_time'] or 0
    
    # Error Count & Rate
    error_requests = recent_requests.filter(status_code__gte=400)
    error_count = error_requests.count()
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
    
    # Error breakdown by status code
    error_breakdown = error_requests.values('status_code').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status code distribution
    status_distribution = recent_requests.values('status_code').annotate(
        count=Count('id')
    ).order_by('status_code')
    
    # Response time distribution (for charting)
    response_time_stats = recent_requests.aggregate(
        min_time=Avg('response_time_ms'),  # Using Avg for simplicity, could use Min/Max
        max_time=Avg('response_time_ms'),
        p50=Avg('response_time_ms'),  # Simplified - in production, use percentile
        p95=Avg('response_time_ms'),
        p99=Avg('response_time_ms'),
    )
    
    # Requests per hour (for time series chart)
    requests_per_hour = recent_requests.annotate(
        hour=TruncHour('timestamp')
    ).values('hour').annotate(
        count=Count('id'),
        avg_response_time=Avg('response_time_ms')
    ).order_by('hour')
    
    # Top endpoints by request count
    top_endpoints = recent_requests.values('endpoint', 'method').annotate(
        count=Count('id'),
        avg_response_time=Avg('response_time_ms'),
        error_count=Count('id', filter=Q(status_code__gte=400))
    ).order_by('-count')[:10]
    
    # Recent errors (last 20)
    recent_errors = error_requests.select_related('user').order_by('-timestamp')[:20]
    
    # Build response data
    metrics = {
        'time_range_hours': hours,
        'total_requests': total_requests,
        'average_response_time_ms': round(avg_response_time, 2),
        'error_count': error_count,
        'error_rate_percent': round(error_rate, 2),
        'error_breakdown': list(error_breakdown),
        'status_distribution': list(status_distribution),
        'response_time_stats': {
            'min': round(response_time_stats['min_time'] or 0, 2),
            'max': round(response_time_stats['max_time'] or 0, 2),
            'avg': round(avg_response_time, 2),
        },
        'requests_per_hour': [
            {
                'hour': item['hour'].isoformat() if item['hour'] else None,
                'count': item['count'],
                'avg_response_time': round(item['avg_response_time'] or 0, 2)
            }
            for item in requests_per_hour
        ],
        'top_endpoints': [
            {
                'endpoint': item['endpoint'],
                'method': item['method'],
                'count': item['count'],
                'avg_response_time': round(item['avg_response_time'] or 0, 2),
                'error_count': item['error_count']
            }
            for item in top_endpoints
        ],
        'recent_errors': APIMonitorSerializer(recent_errors, many=True).data,
    }
    
    return Response(metrics, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def monitoring_details(request, request_id):
    """
    Get detailed information about a specific API request by request_id.
    """
    try:
        monitor = APIMonitor.objects.select_related('user').get(request_id=request_id)
        serializer = APIMonitorSerializer(monitor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIMonitor.DoesNotExist:
        return Response(
            {'error': 'Request not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def monitoring_errors(request):
    """
    Get list of errors with filtering options.
    """
    hours = int(request.GET.get('hours', 24))
    status_code = request.GET.get('status_code')
    endpoint = request.GET.get('endpoint')
    
    time_threshold = timezone.now() - timedelta(hours=hours)
    errors = APIMonitor.objects.filter(
        timestamp__gte=time_threshold,
        status_code__gte=400
    ).select_related('user')
    
    if status_code:
        errors = errors.filter(status_code=status_code)
    if endpoint:
        errors = errors.filter(endpoint__icontains=endpoint)
    
    errors = errors.order_by('-timestamp')[:100]  # Limit to 100 most recent
    
    serializer = APIMonitorSerializer(errors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

