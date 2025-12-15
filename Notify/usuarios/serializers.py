from rest_framework import serializers
from .models import Usuario


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 'bio', 'foto', 'notifPorMail',
                  'notifRecomendaciones', 'notifGenerales', 'password')
        read_only_fields = ('username', )

    def create(self, validated_data):
        # Extraer la contraseña antes de crear el usuario
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'La contraseña es requerida'})
        
        # Crear usuario sin contraseña primero
        user = Usuario.objects.create(**validated_data)
        
        # Hashear y establecer contraseña correctamente
        user.set_password(password)
        user.save()
        
        return user
