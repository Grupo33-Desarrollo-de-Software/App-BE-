from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Log
from .serializers import LogSerializer

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

@api_view
def errorCount(request):
    errors = Log.objects.filter(logtype=ERROR_TYPE).count()

