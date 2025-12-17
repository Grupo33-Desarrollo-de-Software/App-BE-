from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from datetime import datetime, timedelta
from notificaciones.models import Notificacion
from notificaciones.actions import crearNotificacion
from notificaciones.tasks import taskNotificaciones
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista
import notificaciones.actions as actions


User = get_user_model()


class NotificacionesTests(TestCase):
    #clase para testear: Generación, configuración y envío de notificaciones
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            notifPorMail=True,
            notifRecomendaciones=True,
            notifGenerales=True
        )
        
        self.artista = Artista.objects.create(
            name="Test Artist",
            image="http://example.com/artist.jpg",
            listeners=1000,
            plays=5000,
            summary="Test artist summary"
        )
        
        self.album = Album.objects.create(
            title="Test Album",
            tags="rock,pop",
            releaseDate=date(2020, 1, 1),
            length=3600,
            cover="http://example.com/album.jpg",
            playcount=10000,
            autor=self.artista
        )

    @patch("notificaciones.strategies.send_mail")
    def test_send_notification_by_email(self, mock_send_mail):
        titulo = "Test Notification"
        cuerpo = "This is a test notification"
        crearNotificacion(self.user, titulo, cuerpo)
        
        #verificamos q se guardo en la db
        notificacion = Notificacion.objects.filter(
            usuario=self.user,
            titulo=titulo
        ).first()
        self.assertIsNotNone(notificacion)
        self.assertEqual(notificacion.cuerpo, cuerpo)
        
        #verificamos q se le haya enviado el mail
        mock_send_mail.assert_called_once_with(
            titulo,
            cuerpo,
            "notifymusic33@gmail.com",
            [self.user.email],
            fail_silently=False
        )

    def test_configure_notifications(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "notificaciones": {
                "mail": False,
                "recomendaciones": False,
                "generales": True
            }
        }
        response = self.client.post("/api/v1/configurar", data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "datos modificados con éxito")
        
        #verificar que se actualizaron las preferencias
        self.user.refresh_from_db()
        self.assertFalse(self.user.notifPorMail)
        self.assertFalse(self.user.notifRecomendaciones)
        self.assertTrue(self.user.notifGenerales)

        #volvemos a como estaba todo
        data = {
            "notificaciones": {
                "mail": True,
                "recomendaciones": True,
                "generales": True
            }
        }
        response = self.client.post("/api/v1/configurar", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("notificaciones.strategies.send_mail")
    @patch("notificaciones.actions.apiExterna.getTopAlbumsFromArtista")
    @patch("notificaciones.actions.apiExterna.getAlbumsSimilares")
    def test_generate_notifications(self, mock_get_similares, mock_get_top, mock_send_mail):
        #probamos que se generen recomendaciones y avisos 
        
        #le creamos un follow al usuario
        Follow.objects.create(usuario=self.user, album=self.album)

        mock_get_similares.return_value = [
            {
                "titulo": "Album Recomendado 1",
                "artista": "Artista Similar",
                "mbid": "12345",
                "url": "http://example.com"
            },
            {
                "titulo": "Album Recomendado 2",
                "artista": "Artista Similar",
            }
        ]

        #generamos una fecha dinamica para que use para filtrar
        fecha_hoy = datetime.now().strftime("%d %b %Y") 
        
        mock_get_top.return_value = [
            {
                "titulo": "Nuevo Lanzamiento Hit",
                "artista": "Test Artist", 
                "fechaLanzamiento": fecha_hoy, #pasa el filtro que tenemos en actions.py de > semana pasada
                "url": "http://example.com/new"
            }
        ]

        taskNotificaciones()


        #verificamos que se crearon notificaciones en la db
        conteo = Notificacion.objects.filter(usuario=self.user).count()
        self.assertGreater(conteo, 0)

        #verificamos el contenido de las notificaciones
        notif_reco = Notificacion.objects.filter(cuerpo__contains="Album Recomendado 1").first()
        self.assertIsNotNone(notif_reco)
        self.assertEqual(notif_reco.titulo, "Tal vez te gusten los siguientes álbumes 🧐")

        notif_novedad = Notificacion.objects.filter(cuerpo__contains="Nuevo Lanzamiento Hit").first()
        self.assertIsNotNone(notif_novedad)
        self.assertEqual(notif_novedad.titulo, "Deberías chequear los nuevos álbumes de tus artistas favoritos!!!")

        #verificamos el envio de mails
        self.assertTrue(mock_send_mail.called)
        self.assertGreaterEqual(mock_send_mail.call_count, 1)
