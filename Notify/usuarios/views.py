from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Usuario
from .serializers import UserSerializer, UserRegistrationSerializer

from logger.views import logCrud

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
        # Use get_or_create to create token if it doesn't exist
        token, created = Token.objects.get_or_create(user=user)
        if created:
            logCrud(f"Token created for user: {user.username}")
        logCrud(f"User logged in: {user.username}")
        return Response({
            'token': token.key,
            'id': user.pk,
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user. No authentication required.
    Supports both JSON and multipart/form-data (for file uploads).
    Only administrators can set is_staff and is_superuser permissions.
    """
    # Handle both JSON and multipart/form-data
    data = request.data.copy()
    files = request.FILES
    
    # Pass request context to serializer for permission validation
    serializer = UserRegistrationSerializer(data=data, files=files, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        
        # Log registration with admin status if applicable
        admin_status = ""
        if user.is_staff or user.is_superuser:
            admin_status = f" (Admin: staff={user.is_staff}, superuser={user.is_superuser})"
        logCrud(f"New user registered: {user.username}{admin_status}")
        
        return Response({
            'token': token.key,
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        notifRecomendaciones = notificaciones.get("recomendaciones", usuario.notifRecomendaciones)
        notifGenerales = notificaciones.get("generales", usuario.notifGenerales)

        usuario.notifPorMail = notifMail
        usuario.notifRecomendaciones = notifRecomendaciones
        usuario.notifGenerales = notifGenerales

        logCrud(f"El usuario {usuario.username} cambió sus preferencias de notificaciones")

    usuario.save()

    return Response({"success": "datos modificados con éxito"})
