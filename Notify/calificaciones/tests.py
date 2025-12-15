from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import date
from rest_framework.test import APIClient
from calificaciones.models import Rate
from albums.models import Album
from artistas.models import Artista

User = get_user_model()


class CalificacionesTests(TestCase):
    # clase para testear: Calificar y modificar calificaciones de álbumes

    def setUp(self):
        # seteamos al usuario, al artista y 2 albumes del artista
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        self.artista = Artista.objects.create(
            name="Test Artist",
            image="http://example.com/artist.jpg",
            listeners=1000,
            plays=5000,
            summary="Test artist summary",
        )

        self.album = Album.objects.create(
            title="Test Album",
            tags="rock,pop",
            releaseDate=date(2020, 1, 1),
            length=3600,
            cover="http://example.com/album.jpg",
            playcount=10000,
            autor=self.artista,
        )

    @patch("albums.views.logAction")
    @patch("albums.views.parsearFecha")
    @patch("albums.views.api.buscarAlbum")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_rate_album(
        self,
        mock_parsear_artista,
        mock_get_artista,
        mock_buscar_album,
        mock_parsear_fecha,
        mock_log,
    ):
        mock_parsear_artista.return_value = {
            "nombre": "Test Artist",
            "foto": "http://example.com/artist.jpg",
            "resumen": "Test artist summary",
            "oyentes": 1000,
            "reproducciones": 5000,
        }
        mock_get_artista.return_value = {}
        mock_buscar_album.return_value = {
            "titulo": "Test Album",
            "etiquetas": "rock,pop",
            "fechaLanzamiento": "01 Jan 2020",
            "duracion": 3600,
            "foto": "http://example.com/album.jpg",
            "reproducciones": 10000,
        }
        mock_parsear_fecha.return_value = date(2020, 1, 1)

        self.client.force_login(self.user)

        # simula q un usuario lleno el formulario
        response = self.client.post(
            "/api/v1/calificar/Test%20Artist/Test%20Album",
            data={"rate": "5", "comment": "Excelente álbum"},
            HTTP_REFERER="/api/v1/album/Test%20Artist/Test%20Album",
        )

        # verificamos un redirect
        self.assertEqual(response.status_code, 302)

        # verificamos que se creo la calificacion
        rate = Rate.objects.filter(usuario=self.user, album=self.album).first()
        self.assertIsNotNone(rate)
        self.assertEqual(rate.rate, 5)
        self.assertEqual(rate.comment, "Excelente álbum")

        # verificamos el logaction
        mock_log.assert_called_once_with(
            "El usuario testuser calificó el album Test Album"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.parsearFecha")
    @patch("albums.views.api.buscarAlbum")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_modify_rating(
        self,
        mock_parsear_artista,
        mock_get_artista,
        mock_buscar_album,
        mock_parsear_fecha,
        mock_log,
    ):
        Rate.objects.create(
            usuario=self.user, album=self.album, rate=3, comment="Comentario original"
        )

        mock_parsear_artista.return_value = {
            "nombre": "Test Artist",
            "foto": "http://example.com/artist.jpg",
            "resumen": "Test artist summary",
            "oyentes": 1000,
            "reproducciones": 5000,
        }
        mock_get_artista.return_value = {}

        mock_buscar_album.return_value = {
            "titulo": "Test Album",
            "etiquetas": "rock,pop",
            "fechaLanzamiento": "01 Jan 2020",
            "duracion": 3600,
            "foto": "http://example.com/album.jpg",
            "reproducciones": 10000,
        }
        mock_parsear_fecha.return_value = date(2020, 1, 1)

        self.client.force_login(self.user)

        # simula q un usuario lleno el formulario (lo que modifica la calificacion)
        response = self.client.post(
            "/api/v1/calificar/Test%20Artist/Test%20Album",
            data={"rate": "4", "comment": "Comentario modificado"},
            HTTP_REFERER="/api/v1/album/Test%20Artist/Test%20Album",
        )

        self.assertEqual(response.status_code, 302)

        # verifica q se modifico y no que se creo una nueva
        rates = Rate.objects.filter(usuario=self.user, album=self.album)
        self.assertEqual(rates.count(), 1)

        rate = rates.first()
        self.assertEqual(rate.rate, 4)
        self.assertEqual(rate.comment, "Comentario modificado")

        mock_log.assert_called_once_with(
            "El usuario testuser calificó el album Test Album"
        )


class IntegrationTests(TestCase):
    # tests de integración teniendo en cuenta la calificación de un album y su posterior modificacion

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.parsearFecha")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_rate_lifecycle(
        self,
        mock_parsear_artista,
        mock_get_artista,
        mock_buscar_album,
        mock_persistir,
        mock_parsear_fecha,
        mock_log_action,
    ):

        album_title = "Integration Album"
        artist_name = "Integration Artist"

        # configuramos los mocks
        mock_parsear_artista.return_value = {
            "nombre": artist_name,
            "foto": "http://example.com/artist.jpg",
            "resumen": "Artist summary",
            "oyentes": 10,
            "reproducciones": 20,
        }
        mock_get_artista.return_value = {}

        mock_buscar_album.return_value = {
            "titulo": album_title,
            "artista": artist_name,
            "foto": "http://example.com/cover.jpg",
            "fechaLanzamiento": "01 Jan 2023",
            "duracion": 3600,
            "reproducciones": 100,
            "etiquetas": "rock",
        }

        mock_parsear_fecha.return_value = date(2023, 1, 1)

        # creamos los objetos que persistirAlbum devolveria para que la vista los use
        artist_obj = Artista.objects.create(
            name=artist_name,
            image="http://example.com/artist.jpg",
            summary="Artist summary",
            listeners=10,
            plays=20,
        )
        album_obj = Album.objects.create(
            title=album_title,
            autor=artist_obj,
            tags="rock",
            length=3600,
            cover="http://example.com/cover.jpg",
            releaseDate=date(2023, 1, 1),
            playcount=100,
        )

        mock_persistir.return_value = (artist_obj, album_obj)

        self.client.force_login(self.user)

        # paso 1, calificamos
        response_rate = self.client.post(
            "/api/v1/calificar/Integration%20Artist/Integration%20Album",
            data={"rate": "5", "comment": "Good album"},
            HTTP_REFERER="/api/v1/album/Integration%20Artist/Integration%20Album",
        )

        self.assertEqual(response_rate.status_code, 302)

        # verificamos la persistencia en la db
        rate_obj = Rate.objects.filter(usuario=self.user, album=album_obj).first()
        self.assertIsNotNone(rate_obj)
        self.assertEqual(rate_obj.rate, 5)
        self.assertEqual(rate_obj.comment, "Good album")

        mock_log_action.assert_called_once_with(
            f"El usuario testuser calificó el album {album_title}"
        )

        # paso 2, updateamos la calificacion
        # reseteamos el mock
        mock_log_action.reset_mock()

        # enviamos la nueva calificación (mismo usuario, mismo álbum, diferente nota)
        response_update = self.client.post(
            "/api/v1/calificar/Integration%20Artist/Integration%20Album",
            data={"rate": "2", "comment": "Changed my mind"},
            HTTP_REFERER="/api/v1/album/Integration%20Artist/Integration%20Album",
        )

        self.assertEqual(response_update.status_code, 302)

        # nos aseguramos de que no se creo uno nuevo, sino que se actualizó el existente
        self.assertEqual(
            Rate.objects.filter(usuario=self.user, album=album_obj).count(), 1
        )

        # refrescamos desde la db
        rate_obj.refresh_from_db()
        self.assertEqual(rate_obj.rate, 2)
        self.assertEqual(rate_obj.comment, "Changed my mind")

        # verificamos que se logueó la acción nuevamente)
        mock_log_action.assert_called_once_with(
            "El usuario testuser calificó el album Integration Album"
        )
