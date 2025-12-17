from abc import ABC, abstractmethod
from django.core.mail import send_mail
from notificaciones.models import Notificacion


class NotificationStrategy(ABC):
    """
    Interfaz abstracta para las estrategias de notificación.
    Define el contrato que todas las estrategias de notificación deben implementar.
    """

    @abstractmethod
    def can_send(self, usuario):
        """
        Verifica si la estrategia puede enviar notificaciones al usuario.

        Args:
            usuario: Instancia del modelo Usuario

        Returns:
            bool: True si puede enviar, False en caso contrario
        """
        pass

    @abstractmethod
    def send(self, usuario, titulo, cuerpo):
        """
        Envía una notificación al usuario usando esta estrategia.

        Args:
            usuario: Instancia del modelo Usuario
            titulo: Título de la notificación
            cuerpo: Cuerpo/contenido de la notificación

        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        pass


class EmailNotificationStrategy(NotificationStrategy):
    """
    Estrategia para enviar notificaciones por correo electrónico.
    """

    def __init__(self, from_email="notifymusic33@gmail.com"):
        """
        Inicializa la estrategia de email.

        Args:
            from_email: Dirección de correo desde la cual se enviarán las notificaciones
        """
        self.from_email = from_email

    def can_send(self, usuario):
        """
        Verifica si el usuario tiene habilitado el envío por email
        y tiene una dirección de correo configurada.

        Args:
            usuario: Instancia del modelo Usuario

        Returns:
            bool: True si puede enviar email, False en caso contrario
        """
        return usuario.notifPorMail and bool(usuario.email)

    def send(self, usuario, titulo, cuerpo):
        """
        Envía una notificación por correo electrónico.

        Args:
            usuario: Instancia del modelo Usuario
            titulo: Título de la notificación
            cuerpo: Cuerpo/contenido de la notificación

        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        if not self.can_send(usuario):
            return False

        try:
            send_mail(
                titulo,
                cuerpo,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error enviando email a {usuario.email}: {e}")
            return False


class DatabaseNotificationStrategy(NotificationStrategy):
    """
    Estrategia para guardar notificaciones en la base de datos.
    Esta estrategia siempre debe ejecutarse para mantener el historial.
    """

    def can_send(self, usuario):
        """
        Siempre puede guardar en la base de datos.

        Args:
            usuario: Instancia del modelo Usuario

        Returns:
            bool: Siempre True
        """
        return True

    def send(self, usuario, titulo, cuerpo):
        """
        Guarda la notificación en la base de datos.

        Args:
            usuario: Instancia del modelo Usuario
            titulo: Título de la notificación
            cuerpo: Cuerpo/contenido de la notificación

        Returns:
            bool: True si se guardó exitosamente, False en caso contrario
        """
        try:
            Notificacion.objects.create(
                titulo=titulo,
                cuerpo=cuerpo,
                usuario=usuario,
            )
            return True
        except Exception as e:
            print(f"Error guardando notificación en BD para {usuario.username}: {e}")
            return False


class RecommendationNotificationStrategy(NotificationStrategy):
    """
    Estrategia para generar y enviar notificaciones de recomendaciones de álbumes.
    Esta estrategia genera las recomendaciones basándose en los álbumes seguidos
    por el usuario y luego las envía usando otras estrategias de entrega.
    """

    def __init__(self):
        """Inicializa la estrategia de recomendaciones."""
        import random
        from apiExterna import apiExterna
        from followlists.models import Follow
        from albums.models import Album
        from artistas.models import Artista

        self.random = random
        self.apiExterna = apiExterna
        self.Follow = Follow
        self.Album = Album
        self.Artista = Artista

    def can_send(self, usuario):
        """
        Verifica si el usuario tiene habilitado las notificaciones de recomendaciones.

        Args:
            usuario: Instancia del modelo Usuario

        Returns:
            bool: True si puede enviar recomendaciones, False en caso contrario
        """
        return usuario.notifRecomendaciones

    def send(self, usuario, titulo, cuerpo):

        if not self.can_send(usuario):
            return None

        # Obtener los follows del usuario
        follows = self.Follow.objects.filter(usuario=usuario.id)
        if not follows.exists():
            return None

        # Obtener los álbumes seguidos
        albums = []
        for f in follows:
            a = self.Album.objects.filter(id=f.album.id).first()
            if a:
                albums.append(a)

        if not albums:
            return None

        # Obtener los artistas de esos álbumes
        artistas = []
        for a in albums:
            if a and a.autor:
                artista = self.Artista.objects.filter(id=a.autor.id).first()
                if artista:
                    artistas.append(artista)

        if not artistas:
            return None

        # Obtener recomendaciones similares de la API externa
        recomendaciones = []
        for artista in artistas:
            try:
                r = self.apiExterna.getAlbumsSimilares(artista.name)
                if r:
                    recomendaciones.extend(r)
            except Exception as e:
                print(f"Error obteniendo álbumes similares para {artista.name}: {e}")
                continue

        if not recomendaciones:
            return None

        # Aleatorizar y limitar a 5 recomendaciones
        self.random.seed()
        self.random.shuffle(recomendaciones)

        try:
            recomendaciones = recomendaciones[:5]
        except Exception:
            pass

        # Generar título y cuerpo de la notificación
        titulo = "Tal vez te gusten los siguientes álbumes 🧐"
        cuerpo = ""
        for r in recomendaciones:
            cuerpo += f"{r['titulo']} - {r['artista']}<br/>"

        # Enviar usando el contexto de notificaciones
        context = NotificationContext()
        context.add_strategy(DatabaseNotificationStrategy())
        context.add_strategy(EmailNotificationStrategy())

        return context.send_notification(usuario, titulo, cuerpo)


class NotificationContext:
    """
    Contexto que gestiona las estrategias de notificación.
    Permite agregar y ejecutar múltiples estrategias de forma flexible.
    """

    def __init__(self):
        """
        Inicializa el contexto con una lista vacía de estrategias.
        """
        self.strategies = []

    def add_strategy(self, strategy):
        """
        Agrega una estrategia de notificación al contexto.

        Args:
            strategy: Instancia de NotificationStrategy

        Returns:
            NotificationContext: Retorna self para permitir encadenamiento
        """
        if isinstance(strategy, NotificationStrategy):
            self.strategies.append(strategy)
        else:
            raise TypeError(
                "La estrategia debe ser una instancia de NotificationStrategy"
            )
        return self

    def send_notification(self, usuario, titulo, cuerpo):
        """
        Envía una notificación usando todas las estrategias configuradas.

        Args:
            usuario: Instancia del modelo Usuario
            titulo: Título de la notificación
            cuerpo: Cuerpo/contenido de la notificación

        Returns:
            dict: Diccionario con los resultados de cada estrategia
        """
        results = {}

        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            try:
                if strategy.can_send(usuario):
                    success = strategy.send(usuario, titulo, cuerpo)
                    results[strategy_name] = {
                        "success": success,
                        "message": (
                            "Enviado exitosamente" if success else "Error al enviar"
                        ),
                    }
                else:
                    results[strategy_name] = {
                        "success": False,
                        "message": "No se puede enviar (preferencias del usuario o datos faltantes)",
                    }
            except Exception as e:
                results[strategy_name] = {
                    "success": False,
                    "message": f"Error: {str(e)}",
                }

        return results
