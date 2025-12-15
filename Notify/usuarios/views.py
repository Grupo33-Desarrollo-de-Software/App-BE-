from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Usuario
from .serializers import UserSerializer

from logger.views import logCrud


class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserLogIn(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        if created:
            logCrud(f"Token created for user: {user.username}")
        logCrud(f"User logged in: {user.username}")
        return Response(
            {
                "token": token.key,
                "id": user.pk,
                "username": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )


@api_view(["POST"])
def configurar(request):

    usuario = request.user
    if type(usuario) == AnonymousUser:
        return Response({"error": "Login required"})

    print(usuario)

    username = request.data.get("username")
    if username:
        oldname = usuario.username
        usuario.username = username
        logCrud(f"El usuario {oldname} cambió su nombre a {username}")

    password = request.data.get("password")
    if password:
        usuario.set_password(password)
        logCrud(f"El usuario {usuario.username} cambió su contraseña")

    email = request.data.get("email")
    if email:
        usuario.email = email
        logCrud(f"El usuario {usuario.username} cambió su email a {email}")

    bio = request.data.get("bio")
    if bio:
        usuario.bio = bio
        logCrud(f"El usuario {usuario.username} cambió su bio")

    notificaciones = request.data.get("notificaciones")
    if notificaciones:
        notifMail = notificaciones.get("mail", usuario.notifPorMail)
        notifRecomendaciones = notificaciones.get(
            "recomendaciones", usuario.notifRecomendaciones
        )
        notifGenerales = notificaciones.get("generales", usuario.notifGenerales)

        usuario.notifPorMail = notifMail
        usuario.notifRecomendaciones = notifRecomendaciones
        usuario.notifGenerales = notifGenerales

        logCrud(
            f"El usuario {usuario.username} cambió sus preferencias de notificaciones"
        )

    usuario.save()

    return Response({"success": "datos modificados con éxito"})
