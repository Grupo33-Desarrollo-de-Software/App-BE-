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
    
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'bio', 'foto', 
                  'notifPorEmail', 'notifRecomendaciones', 'notifGenerales')
        extra_kwargs = {
            'password': {'write_only': True},
            'bio': {'required': False, 'allow_blank': True},
            'foto': {'required': False},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_username(self, value):
        """Validate username is unique and follows Django's requirements"""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        # Extract password before creating user
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required'})
        
        # Set default values for notification preferences if not provided
        if 'notifPorEmail' not in validated_data:
            validated_data['notifPorEmail'] = True
        if 'notifRecomendaciones' not in validated_data:
            validated_data['notifRecomendaciones'] = True
        if 'notifGenerales' not in validated_data:
            validated_data['notifGenerales'] = True
        
        # Create user without password first
        user = Usuario.objects.create(**validated_data)
        
        # Hash and set password properly
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
        fields = ('id', 'username', 'first_name', 'last_name', 'bio', 'foto', 'notifPorEmail',
                  'notifRecomendaciones', 'notifGenerales', 'password')
        read_only_fields = ('username', )

    def create(self, validated_data):
        # Extract password before creating user
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required'})
        
        # Create user without password first
        user = Usuario.objects.create(**validated_data)
        
        # Hash and set password properly
        user.set_password(password)
        user.save()
        
        return user
