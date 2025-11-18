from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, date
import json

from albums.models import Album
from artistas.models import Artista
from albums.views import persistirAlbum, buscarAlbums, getInfo

User = get_user_model()


class AlbumSearchTests(TestCase):
    """Tests for getAlbum/search albums functionality (buscarAlbums)"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_success(self, mock_buscar_albums, mock_log_action):
        """Test successful album search returns results"""
        # Mock the external API response
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

        # Make request as authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/albums/test%20album")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["titulo"], "Test Album 1")
        self.assertEqual(response.data[1]["titulo"], "Test Album 2")
        mock_buscar_albums.assert_called_once_with("test album")

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_anonymous_user(self, mock_buscar_albums, mock_log_action):
        """Test album search works for anonymous users"""
        mock_results = [
            {
                "titulo": "Test Album",
                "artista": "Test Artist",
                "foto": "http://example.com/photo.jpg",
                "mbid": "12345",
            }
        ]
        mock_buscar_albums.return_value = mock_results

        # Make request as anonymous user
        response = self.client.get("/api/v1/albums/test")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        mock_buscar_albums.assert_called_once_with("test")

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_empty_results(self, mock_buscar_albums, mock_log_action):
        """Test album search with no results"""
        mock_buscar_albums.return_value = []

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/albums/nonexistent")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbums")
    def test_search_albums_special_characters(
        self, mock_buscar_albums, mock_log_action
    ):
        """Test album search with special characters in query"""
        mock_results = [
            {
                "titulo": "Album & More",
                "artista": "Artist/Name",
                "foto": "http://example.com/photo.jpg",
                "mbid": "12345",
            }
        ]
        mock_buscar_albums.return_value = mock_results

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/albums/album%20%26%20more")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_buscar_albums.assert_called_once_with("album & more")


class AlbumInfoTests(TestCase):
    """Tests for getInfo - obtain album information functionality"""

    def setUp(self):
        """Set up test client and user"""
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
        """Test successful retrieval of album information"""
        # Mock the external API response
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

        # Mock persistirAlbum to return artist and album objects
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

        # Make request as authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/album/Test%20Artist/Test%20Album")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Test Album")
        self.assertEqual(response.data["artista"], "Test Artist")
        self.assertEqual(response.data["reproducciones"], "1000000")
        mock_buscar_album.assert_called_once_with("Test Artist", "Test Album")
        mock_persistir.assert_called_once_with("Test Artist", mock_album_data)

    @patch("albums.views.logAction")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    def test_get_album_info_anonymous_user(
        self, mock_buscar_album, mock_persistir, mock_log_action
    ):
        """Test getInfo works for anonymous users"""
        mock_album_data = {
            "titulo": "Test Album",
            "artista": "Test Artist",
            "fechaLanzamiento": "01 Jan 2020",
            "reproducciones": "1000000",
            "oyentes": "50000",
            "info": "Test description",
            "cantidadCanciones": 10,
            "foto": "http://example.com/photo.jpg",
            "etiquetas": "rock",
            "duracion": 40,
        }
        mock_buscar_album.return_value = mock_album_data

        mock_artista = Artista.objects.create(
            name="Test Artist", image="http://example.com/artist.jpg"
        )
        mock_album = Album.objects.create(
            title="Test Album",
            tags="rock",
            length=40,
            cover="http://example.com/photo.jpg",
            autor=mock_artista,
        )
        mock_persistir.return_value = (mock_artista, mock_album)

        # Make request as anonymous user
        response = self.client.get("/api/v1/album/Test%20Artist/Test%20Album")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Test Album")
        mock_buscar_album.assert_called_once_with("Test Artist", "Test Album")
        mock_persistir.assert_called_once()

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbum")
    def test_get_album_info_not_found(self, mock_buscar_album, mock_log_action):
        """Test getInfo when album is not found in external API"""
        # Mock API to raise an exception or return None
        mock_buscar_album.side_effect = Exception("Album not found")

        self.client.force_authenticate(user=self.user)

        # The view should handle the exception gracefully
        with self.assertRaises(Exception):
            response = self.client.get(
                "/api/v1/album/Nonexistent%20Artist/Nonexistent%20Album"
            )


class PersistAlbumTests(TestCase):
    """Tests for persistirAlbum - keep album information in database"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

    @patch("albums.views.logAction")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_new_artist_and_album(
        self, mock_parsear_artista, mock_get_artista, mock_log_action
    ):
        """Test persisting a new album with a new artist"""
        # Mock artist API response
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
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "New Artist",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "50000",
            "reproducciones": "1000000",
            "resumen": "Artist summary",
        }

        # Album data to persist
        album_data = {
            "titulo": "New Album",
            "artista": "New Artist",
            "fechaLanzamiento": "15 Mar 2021",
            "reproducciones": 2000000,  # Integer, not string
            "oyentes": "100000",
            "info": "Album description",
            "cantidadCanciones": 15,
            "foto": "http://example.com/album.jpg",
            "etiquetas": "pop, rock",
            "duracion": 50,
        }

        # Call persistirAlbum
        artista_obj, album_obj = persistirAlbum("New Artist", album_data)

        # Assertions
        self.assertIsNotNone(artista_obj)
        self.assertIsNotNone(album_obj)
        self.assertEqual(artista_obj.name, "New Artist")
        self.assertEqual(album_obj.title, "New Album")
        self.assertEqual(album_obj.tags, "pop, rock")
        self.assertEqual(album_obj.length, 50)
        self.assertEqual(album_obj.playcount, 2000000)

        # Verify objects are in database
        self.assertTrue(Artista.objects.filter(name="New Artist").exists())
        self.assertTrue(Album.objects.filter(title="New Album").exists())

    @patch("albums.views.logAction")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_existing_artist_new_album(
        self, mock_parsear_artista, mock_get_artista, mock_log_action
    ):
        """Test persisting a new album with an existing artist"""
        # Create existing artist
        existing_artist = Artista.objects.create(
            name="Existing Artist",
            image="http://example.com/artist.jpg",
            listeners=30000,
            plays=500000,
            summary="Existing summary",
        )

        # Mock artist API response
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

        # Album data
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

        # Call persistirAlbum
        artista_obj, album_obj = persistirAlbum("Existing Artist", album_data)

        # Assertions
        self.assertEqual(
            artista_obj.id, existing_artist.id
        )  # Should be the same artist
        self.assertEqual(album_obj.title, "New Album by Existing Artist")
        self.assertEqual(album_obj.autor.id, existing_artist.id)

        # Verify only one artist exists
        self.assertEqual(Artista.objects.filter(name="Existing Artist").count(), 1)
        # Verify new album was created
        self.assertTrue(
            Album.objects.filter(title="New Album by Existing Artist").exists()
        )

    @patch("albums.views.logAction")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_existing_album(
        self, mock_parsear_artista, mock_get_artista, mock_log_action
    ):
        """Test persisting an album that already exists (should not create duplicate)"""
        # Create existing artist and album
        # Important: artist must have all fields that get_or_create uses for lookup
        existing_artist = Artista.objects.create(
            name="Test Artist",
            image="http://example.com/artist.jpg",
            summary="Summary",  # Must match what parsearArtista2 returns
        )
        existing_album = Album.objects.create(
            title="Existing Album",
            tags="rock",
            releaseDate=datetime.strptime("01 Jan 2020", "%d %b %Y").date(),
            length=40,
            cover="http://example.com/album.jpg",
            playcount=1000000,
            autor=existing_artist,
        )

        # Mock artist API response
        mock_artista_json = {
            "artist": {
                "name": "Test Artist",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "50000", "playcount": "1000000"},
                "bio": {"summary": "Summary"},
            }
        }
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "Test Artist",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "50000",
            "reproducciones": "1000000",
            "resumen": "Summary",
        }

        # Album data (same as existing - must match all lookup fields exactly)
        album_data = {
            "titulo": "Existing Album",
            "artista": "Test Artist",
            "fechaLanzamiento": "01 Jan 2020",  # Must match existing
            "reproducciones": 1000000,  # Integer, not string - this goes to defaults
            "oyentes": "100000",
            "info": "Updated description",
            "cantidadCanciones": 12,
            "foto": "http://example.com/album.jpg",  # Must match existing
            "etiquetas": "rock",  # Must match existing
            "duracion": 40,  # Must match existing
        }

        # Call persistirAlbum
        artista_obj, album_obj = persistirAlbum("Test Artist", album_data)

        # Assertions
        # Note: get_or_create uses title, tags, releaseDate, length, cover, and autor as lookup fields
        # If all match, it should return the existing album
        self.assertEqual(album_obj.id, existing_album.id)  # Should be the same album
        self.assertEqual(album_obj.title, "Existing Album")

        # Verify only one album exists
        self.assertEqual(Album.objects.filter(title="Existing Album").count(), 1)

    @patch("albums.views.logAction")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_no_release_date(
        self, mock_parsear_artista, mock_get_artista, mock_log_action
    ):
        """Test persisting an album without a release date"""
        # Mock artist API response
        mock_artista_json = {
            "artist": {
                "name": "Artist No Date",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "10000", "playcount": "200000"},
                "bio": {"summary": "Summary"},
            }
        }
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "Artist No Date",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "10000",
            "reproducciones": "200000",
            "resumen": "Summary",
        }

        # Album data without release date
        album_data = {
            "titulo": "Album No Date",
            "artista": "Artist No Date",
            "fechaLanzamiento": None,  # No release date
            "reproducciones": 500000,  # Integer, not string
            "oyentes": "25000",
            "info": "Description",
            "cantidadCanciones": 8,
            "foto": "http://example.com/album.jpg",
            "etiquetas": "electronic",
            "duracion": 30,
        }

        # Call persistirAlbum
        artista_obj, album_obj = persistirAlbum("Artist No Date", album_data)

        # Assertions
        self.assertIsNotNone(album_obj)
        self.assertEqual(album_obj.title, "Album No Date")
        # Should use default date "01 Jan 0001" when fechaLanzamiento is None
        # releaseDate is a DateField, but might be stored as datetime, so convert both to date
        expected_date = datetime.strptime("01 Jan 0001", "%d %b %Y").date()
        actual_date = album_obj.releaseDate
        if isinstance(actual_date, datetime):
            actual_date = actual_date.date()
        self.assertEqual(actual_date, expected_date)

    @patch("albums.views.logAction")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_persist_album_with_release_date(
        self, mock_parsear_artista, mock_get_artista, mock_log_action
    ):
        """Test persisting an album with a valid release date"""
        # Mock artist API response
        mock_artista_json = {
            "artist": {
                "name": "Artist With Date",
                "image": [
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": ""},
                    {"#text": "http://example.com/artist.jpg"},
                ],
                "stats": {"listeners": "20000", "playcount": "400000"},
                "bio": {"summary": "Summary"},
            }
        }
        mock_get_artista.return_value = mock_artista_json
        mock_parsear_artista.return_value = {
            "nombre": "Artist With Date",
            "foto": "http://example.com/artist.jpg",
            "oyentes": "20000",
            "reproducciones": "400000",
            "resumen": "Summary",
        }

        # Album data with release date
        album_data = {
            "titulo": "Album With Date",
            "artista": "Artist With Date",
            "fechaLanzamiento": "25 Dec 2023",
            "reproducciones": 3000000,  # Integer, not string
            "oyentes": "150000",
            "info": "Description",
            "cantidadCanciones": 14,
            "foto": "http://example.com/album.jpg",
            "etiquetas": "classical",
            "duracion": 60,
        }

        # Call persistirAlbum
        artista_obj, album_obj = persistirAlbum("Artist With Date", album_data)

        # Assertions
        self.assertIsNotNone(album_obj)
        self.assertEqual(album_obj.title, "Album With Date")
        # releaseDate is a DateField, but might be stored as datetime, so convert both to date
        expected_date = datetime.strptime("25 Dec 2023", "%d %b %Y").date()
        actual_date = album_obj.releaseDate
        if isinstance(actual_date, datetime):
            actual_date = actual_date.date()
        self.assertEqual(actual_date, expected_date)


class IntegrationTests(TestCase):
    """Integration tests combining multiple functionalities"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.api.buscarAlbum")
    @patch("albums.views.api.getArtista")
    @patch("albums.views.api.parsearArtista2")
    def test_search_then_get_info_then_persist(
        self, mock_parsear_artista, mock_get_artista, mock_buscar_album, mock_log_action
    ):
        """Integration test: search album, get info, and verify persistence"""
        # Mock artist API
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

        # Mock album API
        mock_album_data = {
            "titulo": "Integration Album",
            "artista": "Integration Artist",
            "fechaLanzamiento": "10 May 2022",
            "reproducciones": 2500000,  # Integer, not string
            "oyentes": "125000",
            "info": "Integration album description",
            "cantidadCanciones": 16,
            "foto": "http://example.com/integration.jpg",
            "etiquetas": "fusion",
            "duracion": 55,
        }
        mock_buscar_album.return_value = mock_album_data

        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Step 1: Get album info (which should persist it)
        response = self.client.get(
            "/api/v1/album/Integration%20Artist/Integration%20Album"
        )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Integration Album")

        # Step 2: Verify album was persisted in database
        self.assertTrue(Artista.objects.filter(name="Integration Artist").exists())
        self.assertTrue(Album.objects.filter(title="Integration Album").exists())

        persisted_album = Album.objects.get(title="Integration Album")
        self.assertEqual(persisted_album.tags, "fusion")
        self.assertEqual(persisted_album.length, 55)
        self.assertEqual(persisted_album.playcount, 2500000)
        self.assertEqual(persisted_album.autor.name, "Integration Artist")
