from notificaciones.strategies import (
    NotificationContext,
    DatabaseNotificationStrategy,
    EmailNotificationStrategy,
    RecommendationNotificationStrategy,
    NewAlbumsNotificationStrategy,
)


def crearNotificacion(usuario, titulo, cuerpo):
    context = NotificationContext()
    context.add_strategy(DatabaseNotificationStrategy())
    context.add_strategy(EmailNotificationStrategy())
    context.send_notification(usuario, titulo, cuerpo)


def recomendarAlbums(usuario):
    titulo = ""
    cuerpo = ""

    strategy = RecommendationNotificationStrategy()
    return strategy.send(usuario, titulo, cuerpo)


def nuevoDeArtista(usuario):
    titulo = ""
    cuerpo = ""

    strategy = NewAlbumsNotificationStrategy()
    return strategy.send(usuario, titulo, cuerpo)
