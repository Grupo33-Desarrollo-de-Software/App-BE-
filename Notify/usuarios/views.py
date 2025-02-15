from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Usuario
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view

import logging
l = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserLogIn(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                     context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'username': user.username
        })

@api_view(['POST'])
def configurar(request):

    usuario = request.user
    print(usuario)
    if type(usuario) == AnonymousUser:
        return Response({ "error": "Login required"})

    print(usuario)

    username = request.data.get("username")
    if username:
        oldname = usuario.username
        usuario.username = username
        l.info(f"El usuario {oldname} cambió su nombre a {username}")

    password = request.data.get("password")
    if password:
        usuario.set_password(password)
        l.info(f"El usuario {usuario.username} cambió su contraseña")

    email = request.data.get("email")
    if email:
        usuario.email = email
        l.info(f"El usuario {usuario.username} cambió su email a {email}")

    bio = request.data.get("bio")
    if bio:
        usuario.bio = bio
        l.info(f"El usuario {usuario.username} cambió su bio")

    notificaciones = request.data.get("notificaciones")
    if notificaciones:
        notifMail = notificaciones.get("mail", usuario.notifPorMail)
        notifRecomendaciones = notificaciones.get("recomendaciones", usuario.notifRecomendaciones)
        notifGenerales = notificaciones.get("generales", usuario.notifGenerales)

        usuario.notifPorMail = notifMail
        usuario.notifRecomendaciones = notifRecomendaciones
        usuario.notifGenerales = notifGenerales

        l.info(f"El usuario {usuario.username} cambió sus preferencias de notificaciones")

    usuario.save()

    return Response({"success": "datos modificados con éxito"})
