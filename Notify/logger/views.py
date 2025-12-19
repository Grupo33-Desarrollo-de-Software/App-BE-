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


#función principal de logging que valida el tipo y guarda el log tanto en archivo como en db
def log(logtype, body):
    #valida que el tipo de log sea uno de los permitidos
    if logtype not in VALID_LOGTYPES:
        raise Exception("logtype no válido")

    #formatea el mensaje con el tipo de log y el cuerpo
    logmsg = f"[{logtype}]\t{body}"

    #escribe el log en el archivo de log del sistema
    l.info(logmsg)

    #guarda el log en la db para consultas posteriores
    Log.objects.create(logtype=logtype, body=body)


def logCrud(body):
    log(CRUD_TYPE, body)


def logAction(body):
    log(ACTION_TYPE, body)


#deltatime: tiempo transcurrido, method: método HTTP (GET, POST, etc), route: ruta de la petición
def logResponsetime(deltatime, method, route):
    body = f"{method} {route}: {str(deltatime)}"
    log(RESPONSETIME_TYPE, body)


def logError(body):
    log(ERROR_TYPE, body)


#endpoint POST para crear un log manualmente desde una petición HTTP
#permite que otras aplicaciones o servicios externos envíen logs al sistema
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


#endpoint GET para obtener logs filtrados por tipo
#solo accesible para administradores (IsAdminUser)
@api_view(["GET"])
@permission_classes([IsAdminUser])
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

    #serializa los logs y los retorna en formato JSON
    s = LogSerializer(logs, many=True)
    return Response(s.data)


#endpoint GET del panel de monitoreo de API, solo accesible para administradores
#retorna metricas completas para el monitoreo de la API: tiempos de respuesta, errores, endpoints más usados, etc.
@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_dashboard(request):
    try:
        from logging import getLogger

        logger = getLogger(__name__)
        user = request.user
        logger.info(
            f"Intento de acceso al panel de monitoreo - Usuario: {user.username if hasattr(user, 'username') else 'Anónimo'}, "
            f"is_staff: {user.is_staff if hasattr(user, 'is_staff') else 'N/A'}, "
            f"is_superuser: {user.is_superuser if hasattr(user, 'is_superuser') else 'N/A'}, "
            f"is_authenticated: {user.is_authenticated if hasattr(user, 'is_authenticated') else 'N/A'}"
        )

        #obtiene el rango de tiempo desde el parámetro GET (por defecto: últimas 24 horas)
        hours = int(request.GET.get("hours", 24))
        #calcula el umbral de tiempo desde el cual se analizarán las peticiones
        time_threshold = timezone.now() - timedelta(hours=hours)

        #filtra los registros de monitoreo de API dentro del rango de tiempo especificado
        recent_requests = APIMonitor.objects.filter(timestamp__gte=time_threshold)

        #calcula el conteo total de solicitudes en el período
        total_requests = recent_requests.count()

        #calcula el tiempo promedio de respuesta de todas las peticiones
        avg_response_time = (
            recent_requests.aggregate(avg_time=Avg("response_time_ms"))["avg_time"] or 0
        )

        #filtra las peticiones con código de estado >= 400 (errores)
        error_requests = recent_requests.filter(status_code__gte=400)

        #cuenta el total de errores
        error_count = error_requests.count()

        #calcula el porcentaje de errores sobre el total de peticiones
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0

        #desglose de errores agrupados por código de estado (404, 500, etc.) ordenados por cantidad
        error_breakdown = (
            error_requests.values("status_code")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        #distribucion completa de codigos de estado HTTP (200, 201, 404, 500, etc.) ordenados por código
        status_distribution = (
            recent_requests.values("status_code")
            .annotate(count=Count("id"))
            .order_by("status_code")
        )

        #obtiene los 10 endpoints mas utilizados con sus métricas: conteo, tiempo promedio y cantidad de errores
        top_endpoints = (
            recent_requests.values("endpoint", "method")
            .annotate(
                count=Count("id"),
                avg_response_time=Avg("response_time_ms"),
                error_count=Count("id", filter=Q(status_code__gte=400)),
            )
            .order_by("-count")[:10]
        )

        #obtiene los últimos 20 errores con información del usuario que los causó
        recent_errors = error_requests.select_related("user").order_by("-timestamp")[
            :20
        ]

        #construye el diccionario con todas las métricas para retornar al frontend
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
        #registra el error en el log del sistema para depuración
        from logging import getLogger

        logger = getLogger(__name__)
        logger.error(f"Error en monitoring_dashboard: {str(e)}", exc_info=True)

        #retorna un error al cliente (con detalles solo si está en modo DEBUG)
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


#endpoint GET para obtener los detalles completos de una petición específica por su ID
#solo accesible para administradores, útil para investigar problemas específicos
@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_details(request, request_id):
    try:
        #obtiene el registro de monitoreo con la información del usuario relacionado
        #select_related optimiza la consulta cargando el usuario en la misma query
        monitor = APIMonitor.objects.select_related("user").get(request_id=request_id)
        #serializa los datos del registro
        serializer = APIMonitorSerializer(monitor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIMonitor.DoesNotExist:
        #retorna error 404 si no se encuentra la petición
        return Response(
            {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
        )


#endpoint GET para obtener la lista de errores con opciones de filtrado
#solo accesible para administradores, permite filtrar por tiempo, código de estado y endpoint
@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_errors(request):
    #obtiene el rango de tiempo desde el parámetro GET (por defecto: últimas 24 horas)
    hours = int(request.GET.get("hours", 24))
    #obtiene el código de estado opcional para filtrar (ej: 404, 500)
    status_code = request.GET.get("status_code")
    #obtiene el endpoint opcional para filtrar (búsqueda parcial, case-insensitive)
    endpoint = request.GET.get("endpoint")

    #calcula el umbral de tiempo
    time_threshold = timezone.now() - timedelta(hours=hours)
    #filtra errores (status_code >= 400) dentro del rango de tiempo y carga el usuario relacionado
    errors = APIMonitor.objects.filter(
        timestamp__gte=time_threshold, status_code__gte=400
    ).select_related("user")

    #aplica filtro adicional por código de estado si se proporciona
    if status_code:
        errors = errors.filter(status_code=status_code)
    #aplica filtro adicional por endpoint si se proporciona (búsqueda parcial)
    if endpoint:
        errors = errors.filter(endpoint__icontains=endpoint)

    #ordena por timestamp descendente y limita a los 100 errores más recientes
    errors = errors.order_by("-timestamp")[:100]

    #serializa y retorna los errores
    serializer = APIMonitorSerializer(errors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#endpoint GET para obtener las últimas entradas de la bitácora (logs del sistema)
#solo accesible para administradores, retorna los últimos 100 logs ordenados por fecha
@api_view(["GET"])
@permission_classes([IsAdminUser])
def monitoring_logs(request):
    try:
        #obtiene todos los logs, los ordena por fecha descendente y limita a los 100 más recientes
        logs = Log.objects.all().order_by("-datetime")[:100]
        #serializa los logs para retornarlos en formato JSON
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        #maneja cualquier error y retorna un mensaje apropiado
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
