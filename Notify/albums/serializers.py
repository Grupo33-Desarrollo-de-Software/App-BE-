from rest_framework import serializers
from .models import Album


class AlbumSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source="title")
    etiquetas = serializers.CharField(source="tags")
    fechaLanzamiento = serializers.CharField(source="releaseDate")
    duracion = serializers.IntegerField(source="length")
    foto = serializers.CharField(source="cover")
    reproducciones = serializers.IntegerField(source="playcount")
    artista = serializers.CharField(source="autor.name")

    class Meta:
        model = Album
        fields = ['titulo', 'etiquetas','fechaLanzamiento','duracion','foto','reproducciones','artista']
