from rest_framework import serializers
from django.contrib.auth.hashers import make_password
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
        fields = ('id', 'username', 'first_name', 'last_name', 'bio', 'foto', 'notifPorEmail',
                  'notifRecomendaciones', 'notifGenerales')
        read_only_fields = ('username', )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
