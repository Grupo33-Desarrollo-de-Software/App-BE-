from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=True, max_length=150)
    is_staff = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'bio', 'foto', 
                  'notifPorMail', 'notifRecomendaciones', 'notifGenerales', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'password': {'write_only': True},
            'bio': {'required': False, 'allow_blank': True},
            'foto': {'required': False},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'is_staff': {'required': False},
            'is_superuser': {'required': False},
        }

    def validate_username(self, value):
        # Validar que el nombre de usuario sea único y siga los requisitos de Django
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Se requiere una contraseña'})
        
        # Obtener usuario de la solicitud del contexto para verificar permisos
        request = self.context.get('request')
        is_admin = request and (request.user.is_staff or request.user.is_superuser) if request else False
        
        # Extraer campos de los permisos
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)
        
        # Solo permitir a los administradores establecer permisos
        if (is_staff or is_superuser) and not is_admin:
            raise serializers.ValidationError({
                'is_staff': 'Solo los administradores pueden asignar estado de staff.',
                'is_superuser': 'Solo los administradores pueden asignar estado de superusuario.'
            })
        
        # Establecer valores por defecto        
        if 'notifPorMail' not in validated_data:
            validated_data['notifPorMail'] = True
        if 'notifRecomendaciones' not in validated_data:
            validated_data['notifRecomendaciones'] = True
        if 'notifGenerales' not in validated_data:
            validated_data['notifGenerales'] = True
        
        # Crear usuario sin contraseña primero
        user = Usuario.objects.create(**validated_data)
        
        # Establecer permisos si se proporcionan y el usuario es admin
        if is_admin:
            user.is_staff = is_staff
            user.is_superuser = is_superuser
        
        # Hashear y establecer contraseña correctamente
        user.set_password(password)
        user.save()
        
        return user

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
