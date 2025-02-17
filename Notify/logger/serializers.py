from rest_framework import serializers

from .models import Log

class LogSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="logtype")
    cuerpo = serializers.CharField(source="body")

    class Meta:
        model = Log
        fields = ["tipo", "cuerpo"]
