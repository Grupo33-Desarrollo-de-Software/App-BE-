from rest_framework import serializers

from .models import Log

class LogSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="logtype")
    cuerpo = serializers.CharField(source="body")
    fechahora = serializers.CharField(source="datetime")

    class Meta:
        model = Log
        fields = ["tipo", "cuerpo", "fechahora"]
