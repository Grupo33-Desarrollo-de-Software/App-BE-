from abc import ABC, abstractmethod
from django.core.mail import send_mail
from notificaciones.models import Notificacion

#basado en el patron strategy, para permitir que se puedan agregar varios tipos de notifs sin cambiar 
#el codigo en las otras partes

class NotificationStrategy(ABC):
    #interfaz abstracta para las estrategias de notificación

    @abstractmethod
    def can_send(self, usuario):
        #verifica si puede enviar notifs al usuario
        pass

    @abstractmethod
    def send(self, usuario, titulo, cuerpo):
        #envia una notif al usuario usando la estrategia 
        pass


class EmailNotificationStrategy(NotificationStrategy):
    #estrategia para enviar notifs por email
    def __init__(self, from_email="notifymusic33@gmail.com"):
        self.from_email = from_email

    def can_send(self, usuario):
        return usuario.notifPorMail and bool(usuario.email)

    def send(self, usuario, titulo, cuerpo):
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
    #estrategia para guardar las notifs en la db
    def can_send(self, usuario):
        return True

    def send(self, usuario, titulo, cuerpo):
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
    def __init__(self):
        import random
        import apiExterna.apiExterna as api
        from followlists.models import Follow
        from albums.models import Album
        from artistas.models import Artista

        self.random = random
        self.apiExterna = api
        self.Follow = Follow
        self.Album = Album
        self.Artista = Artista

    def can_send(self, usuario):
        return usuario.notifRecomendaciones

    def send(self, usuario, titulo, cuerpo):

        if not self.can_send(usuario):
            return None

        #obtengo los follows del usuario
        follows = self.Follow.objects.filter(usuario=usuario.id)
        if not follows.exists():
            return None

        #obtengo, de los follow,s los álbumes seguidos
        albums = []
        for f in follows:
            a = self.Album.objects.filter(id=f.album.id).first()
            if a:
                albums.append(a)

        if not albums:
            return None

        #obtengo los artistas de dichos albumes 
        artistas = []
        for a in albums:
            if a and a.autor:
                artista = self.Artista.objects.filter(id=a.autor.id).first()
                if artista:
                    artistas.append(artista)

        if not artistas:
            return None

        #obtengo recomendaciones de la api externa
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

        #aleatorizo las recomendaciones
        self.random.seed()
        self.random.shuffle(recomendaciones)

        try:
            #agarro solo 5
            recomendaciones = recomendaciones[:5]
        except Exception:
            pass

        #genero la notif en si
        titulo = "Tal vez te gusten los siguientes álbumes 🧐"
        cuerpo = ""
        for r in recomendaciones:
            cuerpo += f"{r['titulo']} - {r['artista']}<br/>"

        context = NotificationContext()
        context.add_strategy(DatabaseNotificationStrategy())
        context.add_strategy(EmailNotificationStrategy())

        return context.send_notification(usuario, titulo, cuerpo)


class NewAlbumsNotificationStrategy(NotificationStrategy):
    #estrategia para notificar sobre nuevos álbumes de artistas seguidos
    def __init__(self):
        import apiExterna.apiExterna as api
        from followlists.models import Follow
        from albums.models import Album
        from artistas.models import Artista
        from datetime import datetime, timedelta

        self.apiExterna = api
        self.Follow = Follow
        self.Album = Album
        self.Artista = Artista
        self.datetime = datetime
        self.timedelta = timedelta

    def can_send(self, usuario):
        return usuario.notifGenerales

    def send(self, usuario, titulo, cuerpo):
        if not self.can_send(usuario):
            return None

        #obtengo los follows del usuario
        follows = self.Follow.objects.filter(usuario=usuario.id)
        if not follows.exists():
            return None

        #obtengo los álbumes seguidos
        albums = []
        for f in follows:
            a = self.Album.objects.filter(id=f.album.id).first()
            if a:
                albums.append(a)

        if not albums:
            return None

        #obtengo los artistas de dichos álbumes
        artistas = []
        for a in albums:
            if a and a.autor:
                artista = self.Artista.objects.filter(id=a.autor.id).first()
                if artista:
                    artistas.append(artista)

        if not artistas:
            return None

        #obtengo nuevos álbumes de la api externa
        nuevos = []
        for artista in artistas:
            try:
                top = self.apiExterna.getTopAlbumsFromArtista(artista.name)
                if top:
                    for album in top:
                        try:
                            if album.get("fechaLanzamiento"):
                                fecha = self.datetime.strptime(
                                    album["fechaLanzamiento"], "%d %b %Y"
                                )
                                semanaPasada = self.datetime.today() - self.timedelta(days=7)
                                if fecha > semanaPasada:
                                    nuevos.append(album)
                        except (ValueError, KeyError) as e:
                            print(f"Error parseando fecha del álbum: {e}")
                            continue
            except Exception as e:
                print(f"Error obteniendo top álbumes para {artista.name}: {e}")
                continue

        if not nuevos:
            return None

        #genero la notif en si
        titulo = "Deberías chequear los nuevos álbumes de tus artistas favoritos!!!"
        cuerpo = ""
        for n in nuevos:
            cuerpo += f"{n['titulo']} - {n['artista']}<br/>"

        context = NotificationContext()
        context.add_strategy(DatabaseNotificationStrategy())
        context.add_strategy(EmailNotificationStrategy())

        return context.send_notification(usuario, titulo, cuerpo)


class NotificationContext:
    #contexto q permite gestionar (agregar y ejecutar) las estrategias de notifs
    
    def __init__(self):
        #inicializo la lista de estrategias
        self.strategies = []

    def add_strategy(self, strategy):
        #agrego una estrategia. me fijo que sea una instancia de NotificationStrategy
        if isinstance(strategy, NotificationStrategy):
            self.strategies.append(strategy)
        else:
            raise TypeError(
                "La estrategia debe ser una instancia de NotificationStrategy"
            )
        return self

    def send_notification(self, usuario, titulo, cuerpo):
        #envio la notif usando todas las estrategias configuradas
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
