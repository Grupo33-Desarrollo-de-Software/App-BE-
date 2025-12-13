from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, date
from albums.models import Album
from artistas.models import Artista
from albums.views import persistirAlbum, buscarAlbums, getInfo
import json

User = get_user_model()

#no hay q borrar las cosas dsp porq el testcase de djago los borra despues


class AlbumGetInfoTest(TestCase):
    #clase para testear: Obtener info. de albumes
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    def test_get_album_info_success(
        self, mock_buscar_album, mock_persistir, mock_log_action
    ):
        mock_album_data = {
            "titulo": "Test Album",
            "artista": "Test Artist",
            "fechaLanzamiento": "01 Jan 2020",
            "reproducciones": "1000000",
            "oyentes": "50000",
            "info": "This is a test album description",
            "cantidadCanciones": 12,
            "foto": "http://example.com/photo.jpg",
            "etiquetas": "rock, pop",
            "duracion": 45,
        }
        mock_buscar_album.return_value = mock_album_data

        mock_artista = Artista.objects.create(
            name="Test Artist",
            image="http://example.com/artist.jpg",
            listeners=50000,
            plays=1000000,
            summary="Test artist summary",
        )
        mock_album = Album.objects.create(
            title="Test Album",
            tags="rock, pop",
            releaseDate=datetime.strptime("01 Jan 2020", "%d %b %Y").date(),
            length=45,
            cover="http://example.com/photo.jpg",
            playcount=1000000,
            autor=mock_artista,
        )
        mock_persistir.return_value = (mock_artista, mock_album)

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/album/Test%20Artist/Test%20Album")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Test Album")
        self.assertEqual(response.data["artista"], "Test Artist")
        self.assertEqual(response.data["reproducciones"], "1000000")
        mock_buscar_album.assert_called_once_with("Test Artist", "Test Album")
        mock_persistir.assert_called_once_with("Test Artist", mock_album_data)
        mock_log_action.assert_called_once_with("El usuario testuser obtuvo información de test")


    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbum")
    def test_get_album_info_not_found(self, mock_buscar_album, mock_log_action):
        mock_buscar_album.side_effect = Exception("Album not found")

        self.client.force_authenticate(user=self.user)

        with self.assertRaises(Exception):
            response = self.client.get("/api/v1/album/Nonexistent%20Artist/Nonexistent%20Album")


class AlbumSearchTest(TestCase):
    #clase para testear: Buscar álbumes
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    #el patch es para que actuen como el método que se utilizó en views, sin tener que llamar a esa función en si
    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_success(self, mock_buscar_albums, mock_log_action):
        #mock de la respuesta de la API
        mock_results = [
            {
                "titulo": "Test Album 1",
                "artista": "Test Artist 1",
                "foto": "http://example.com/photo1.jpg",
                "mbid": "12345",
            },
            {
                "titulo": "Test Album 2",
                "artista": "Test Artist 2",
                "foto": "http://example.com/photo2.jpg",
                "mbid": "67890",
            },
        ]
        mock_buscar_albums.return_value = mock_results

        #mandamos una request con el user autenticado
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/albums/test%20album")

        #nos fijamos q este todo igual
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["titulo"], "Test Album 1")
        self.assertEqual(response.data[1]["titulo"], "Test Album 2")
        mock_buscar_albums.assert_called_once_with("test album")
        #nos fijamos q log_action fue llamada una vez con lo q esta en el str
        mock_log_action.assert_called_once_with("El usuario testuser buscó test")

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_anonymous_user(self, mock_buscar_albums, mock_log_action):
        #mock de la respuesta de la API
        mock_results = [
            {
                "titulo": "Test Album",
                "artista": "Test Artist",
                "foto": "http://example.com/photo.jpg",
                "mbid": "12345",
            }
        ]
        mock_buscar_albums.return_value = mock_results

        #mandamos una request sin el user autenticado
        response = self.client.get("/api/v1/albums/test")

        #nos fijamos q este todo igual
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        #se fija q se haya llamado UNA vez y con el "test" que sale del apiv1albumstest de arriba
        mock_buscar_albums.assert_called_once_with("test")
        #el "un usuario etc" sale del log_action en views 
        mock_log_action.assert_called_once_with("Un usuario anónimo buscó test")


class AlbumPersistInfoTest(TestCase):
    #clase para testear: Persistir info. de álbumes
    #testeamos persistir info del album cuando hay un nuevo album y artista y cuando solamente hay nuevo album
    def setUp(self):
        self.client = APIClient()

    @patch("albums.views.logCrud")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_new_artist_and_album(
        self, mock_parsear_artista, mock_get_artista, mock_log_crud
    ):
        #mockeamos la rta de la api
        mock_artista_json = {
            "artist": {
                "name": "New Artist",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "50000", "playcount": "1000000"},
                "bio": {"summary": "Artist summary"},
            }
        }
        #se lo pasamos al mock
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "New Artist",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "50000",
            "reproducciones": "1000000",
            "resumen": "Artist summary",
        }

        #la data del album q hay q guardar
        album_data = {
            "titulo": "New Album",
            "artista": "New Artist",
            "fechaLanzamiento": "15 Mar 2021",
            "reproducciones": 2000000,  
            "oyentes": "100000",
            "info": "Album description",
            "cantidadCanciones": 15,
            "foto": "http://example.com/album.jpg",
            "etiquetas": "pop, rock",
            "duracion": 50,
        }

        artista_obj, album_obj = persistirAlbum("New Artist", album_data)

        #nos fijamos q este todo bien
        self.assertIsNotNone(artista_obj)
        self.assertIsNotNone(album_obj)
        self.assertEqual(artista_obj.name, "New Artist")
        self.assertEqual(album_obj.title, "New Album")
        self.assertEqual(album_obj.tags, "pop, rock")
        self.assertEqual(album_obj.length, 50)
        self.assertEqual(album_obj.playcount, 2000000)

        #nos fijamos q esten en la db
        self.assertTrue(Artista.objects.filter(name="New Artist").exists())
        self.assertTrue(Album.objects.filter(title="New Album").exists())
        mock_log_crud.assert_called_once_with("El album New Album fue agregado a la base de datos.")

    @patch("albums.views.logCrud")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_existing_artist_new_album(
        self, mock_parsear_artista, mock_get_artista, mock_log_crud
    ):
        #lo mismo q el de arriba pero con un artista q ya existe
        #creamos dicho artista
        existing_artist = Artista.objects.create(
            name="Existing Artist",
            image="http://example.com/artist.jpg",
            listeners=30000,
            plays=500000,
            summary="Existing summary",
        )

        #mockeamos la rta de la api
        mock_artista_json = {
            "artist": {
                "name": "Existing Artist",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "30000", "playcount": "500000"},
                "bio": {"summary": "Existing summary"},
            }
        }
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "Existing Artist",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "30000",
            "reproducciones": "500000",
            "resumen": "Existing summary",
        }

        #data del album
        album_data = {
            "titulo": "New Album by Existing Artist",
            "artista": "Existing Artist",
            "fechaLanzamiento": "20 Jun 2022",
            "reproducciones": 1500000,  # Integer, not string
            "oyentes": "75000",
            "info": "New album description",
            "cantidadCanciones": 10,
            "foto": "http://example.com/newalbum.jpg",
            "etiquetas": "jazz",
            "duracion": 35,
        }

        artista_obj, album_obj = persistirAlbum("Existing Artist", album_data)

        #assertions de q todo este bien
        self.assertEqual(
            artista_obj.id, existing_artist.id
        )  # Should be the same artist
        self.assertEqual(album_obj.title, "New Album by Existing Artist")
        self.assertEqual(album_obj.autor.id, existing_artist.id)

        #nos fijamos q haya un solo artista en la db, q no lo haya agregado
        self.assertEqual(Artista.objects.filter(name="Existing Artist").count(), 1)

        #nos fijamos q haya un nuevo album en la db
        self.assertTrue(
            Album.objects.filter(title="New Album by Existing Artist").exists()
        )
        mock_log_crud.assert_called_once_with("El album New Album by Existing Artist fue agregado a la base de datos.")


class IntegrationTests(TestCase):
    #tests de integración teniendo en cuenta la busqueda de un álbum, obtener info y guardarla en la db
   
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.logCrud")
    @patch("albums.views.api.buscarAlbum")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_search_then_get_info_then_persist(
        self, mock_parsear_artista, mock_get_artista, mock_buscar_album, mock_log_action, mock_log_crud
    ):
        mock_artista_json = {
            "artist": {
                "name": "Integration Artist",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "60000", "playcount": "1200000"},
                "bio": {"summary": "Integration summary"},
            }
        }
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "Integration Artist",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "60000",
            "reproducciones": "1200000",
            "resumen": "Integration summary",
        }

        mock_album_data = {
            "titulo": "Integration Album",
            "artista": "Integration Artist",
            "fechaLanzamiento": "10 May 2022",
            "reproducciones": 2500000,  
            "oyentes": "125000",
            "info": "Integration album description",
            "cantidadCanciones": 16,
            "foto": "http://example.com/integration.jpg",
            "etiquetas": "fusion",
            "duracion": 55,
        }
        mock_buscar_album.return_value = mock_album_data

        self.client.force_authenticate(user=self.user)

        #buscamos la info del album, lo que la termina guardando en la db
        response = self.client.get(
            "/api/v1/album/Integration%20Artist/Integration%20Album"
        )

        #assertions de q todo este bien
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Integration Album")

        #assertions de q se guarde en la db
        self.assertTrue(Artista.objects.filter(name="Integration Artist").exists())
        self.assertTrue(Album.objects.filter(title="Integration Album").exists())

        #lo obtenemos de la db y nos fijamos q este todo bien
        persisted_album = Album.objects.get(title="Integration Album")
        self.assertEqual(persisted_album.tags, "fusion")
        self.assertEqual(persisted_album.length, 55)
        self.assertEqual(persisted_album.playcount, 2500000)
        self.assertEqual(persisted_album.autor.name, "Integration Artist")

        #nos fijamos q los logs esten bien
        mock_log_action.assert_called_once_with("El usuario testuser obtuvo información de Integration Album")
        mock_log_crud.assert_called_once_with("El album Integration Album fue agregado a la base de datos.")
