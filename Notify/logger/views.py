from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db.models import Count, Avg, Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import status
from .models import Log, APIMonitor
from .serializers import (
    LogSerializer,
    APIMonitorSerializer,
    MonitoringMetricsSerializer,
)

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


@api_view(["POST"])
def logview(request):

    logtype = request.data.get("logtype")
    if not logtype or logtype not in VALID_LOGTYPES:
        return Response(
            {
                "error": "logtype required. Valid logtypes are CRUD, ACTION RESPONSETIME and ERROR"
            }
        )
    body = request.data.get("body")
    if not body:
        return Response({"error": "body required"})

    log(logtype, body)

    return Response({"success": "log created succesfully"})


@api_view(["GET"])
@permission_classes([AllowAny])
def getlogs(request, logtype):

    logs = []

    logtype = logtype.upper()

    if logtype in VALID_LOGTYPES:
        logs = Log.objects.filter(logtype=logtype)
    elif logtype == ANY_TYPE:
        logs = Log.objects.all()
    else:
        return Response(
            {
                "error": "logtype required. Valid logtypes are CRUD, ACTION, RESPONSETIME, ERROR and ANY"
            }
        )

    s = LogSerializer(logs, many=True)
    return Response(s.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_dashboard(request):
    # Endpoint del panel de monitoreo de API solo para administradores.
    # Retorna métricas completas para el monitoreo de salud de la API.
    try:
        # Registrar información del usuario
        from logging import getLogger

        logger = getLogger(__name__)
        user = request.user
        logger.info(
            f"Intento de acceso al panel de monitoreo - Usuario: {user.username if hasattr(user, 'username') else 'Anónimo'}, "
            f"is_staff: {user.is_staff if hasattr(user, 'is_staff') else 'N/A'}, "
            f"is_superuser: {user.is_superuser if hasattr(user, 'is_superuser') else 'N/A'}, "
            f"is_authenticated: {user.is_authenticated if hasattr(user, 'is_authenticated') else 'N/A'}"
        )

        # Obtener rango de tiempo (por defecto: últimas 24 horas)
        hours = int(request.GET.get("hours", 24))
        time_threshold = timezone.now() - timedelta(hours=hours)

        # Filtrar registros de monitoreo de API dentro del rango de tiempo
        recent_requests = APIMonitor.objects.filter(timestamp__gte=time_threshold)

        # Conteo total de solicitudes
        total_requests = recent_requests.count()

        # Tiempo promedio de respuesta
        avg_response_time = (
            recent_requests.aggregate(avg_time=Avg("response_time_ms"))["avg_time"] or 0
        )

        # Conteo y tasa de errores
        error_requests = recent_requests.filter(status_code__gte=400)
        error_count = error_requests.count()
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0

        # Desglose de errores por código de estado
        error_breakdown = (
            error_requests.values("status_code")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Distribución de códigos de estado
        status_distribution = (
            recent_requests.values("status_code")
            .annotate(count=Count("id"))
            .order_by("status_code")
        )

        # Endpoints principales por conteo de solicitudes
        top_endpoints = (
            recent_requests.values("endpoint", "method")
            .annotate(
                count=Count("id"),
                avg_response_time=Avg("response_time_ms"),
                error_count=Count("id", filter=Q(status_code__gte=400)),
            )
            .order_by("-count")[:10]
        )

        # Errores recientes (últimos 20)
        recent_errors = error_requests.select_related("user").order_by("-timestamp")[
            :20
        ]

        # Construir datos de respuesta
        metrics = {
            "time_range_hours": hours,
            "total_requests": total_requests,
            "average_response_time_ms": round(avg_response_time, 2),
            "error_count": error_count,
            "error_rate_percent": round(error_rate, 2),
            "error_breakdown": list(error_breakdown),
            "status_distribution": list(status_distribution),
            "top_endpoints": [
                {
                    "endpoint": item["endpoint"],
                    "method": item["method"],
                    "count": item["count"],
                    "avg_response_time": round(item["avg_response_time"] or 0, 2),
                    "error_count": item["error_count"],
                }
                for item in top_endpoints
            ],
            "recent_errors": APIMonitorSerializer(recent_errors, many=True).data,
        }

        return Response(metrics, status=status.HTTP_200_OK)

    except Exception as e:
        # Registrar el error para depuración
        from logging import getLogger

        logger = getLogger(__name__)
        logger.error(f"Error en monitoring_dashboard: {str(e)}", exc_info=True)

        # Retornar error
        return Response(
            {
                "error": "Ocurrió un error al cargar los datos de monitoreo",
                "detail": (
                    str(e)
                    if settings.DEBUG
                    else "Por favor verifique los logs del servidor"
                ),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_details(request, request_id):
    try:
        monitor = APIMonitor.objects.select_related("user").get(request_id=request_id)
        serializer = APIMonitorSerializer(monitor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIMonitor.DoesNotExist:
        return Response(
            {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_errors(request):
    #obtenemos la lista de errores con opciones de filtrado
    hours = int(request.GET.get("hours", 24))
    status_code = request.GET.get("status_code")
    endpoint = request.GET.get("endpoint")

    time_threshold = timezone.now() - timedelta(hours=hours)
    errors = APIMonitor.objects.filter(
        timestamp__gte=time_threshold, status_code__gte=400
    ).select_related("user")

    if status_code:
        errors = errors.filter(status_code=status_code)
    if endpoint:
        errors = errors.filter(endpoint__icontains=endpoint)

    errors = errors.order_by("-timestamp")[:100]  # Limitar a los 100 más recientes

    serializer = APIMonitorSerializer(errors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_logs(request):
    #obtenemos las últimas 100 entradas de la bitácora.
    try:
        logs = Log.objects.all().order_by("-datetime")[:100]
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {
                "error": "Error al obtener las entradas de la bitácora",
                "detail": (
                    str(e)
                    if settings.DEBUG
                    else "Por favor verifique los logs del servidor"
                ),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
