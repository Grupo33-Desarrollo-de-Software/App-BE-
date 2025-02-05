from rest_framework import serializers
from .models import Usuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 'bio', 'foto', 'notifPorEmail',
                  'notifRecomendaciones', 'notifGenerales')
        read_only_fields = ('username', )