from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from followlists.models import Follow
from albums.models import Album
from artistas.models import Artista

User = get_user_model()

class FollowListTests(TestCase):
    #clase para testear: Obtener, agregar y eliminar álbumes de la lista de seguimiento

    def setUp(self):
        #seteamos al usuario, al artista y 2 albumes del artista
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        
        self.artista = Artista.objects.create(
            name="Test Artist",
            image="http://example.com/artist.jpg",
            listeners=1000,
            plays=5000,
            summary="Test artist summary"
        )
        
        self.album1 = Album.objects.create(
            title="Test Album 1",
            tags="rock,pop",
            releaseDate=date(2020, 1, 1),
            length=3600,
            cover="http://example.com/album1.jpg",
            playcount=10000,
            autor=self.artista
        )
        
        self.album2 = Album.objects.create(
            title="Test Album 2",
            tags="jazz,blues",
            releaseDate=date(2021, 5, 15),
            length=2400,
            cover="http://example.com/album2.jpg",
            playcount=5000,
            autor=self.artista
        )

    def test_get_follow_list(self):
        #creamos los follows
        Follow.objects.create(usuario=self.user, album=self.album1)
        Follow.objects.create(usuario=self.user, album=self.album2)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/v1/followlist/{self.user.username}")
        
        #verificamos que lo que obtenemos de la followlist sea igual a lo que esperamos
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["titulo"], "Test Album 1")
        self.assertEqual(response.data[1]["titulo"], "Test Album 2")
        self.assertEqual(response.data[0]["artista"], "Test Artist")

    @patch("albums.views.logAction")
    @patch("albums.views.crearNotificacion")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    def test_add_album_to_follow_list(
        self, mock_buscar_album, mock_persistir, mock_notif, mock_log
    ):
        #mockeamos la rta de la api al album
        mock_album_data = {
            "titulo": "New Album",
            "artista": "New Artist",
            "foto": "http://example.com/new.jpg",
            "fechaLanzamiento": "01 Jan 2023",
            "duracion": 3000,
            "reproducciones": 15000,
            "etiquetas": "rock"
        }
        mock_buscar_album.return_value = mock_album_data
        
        artista_nuevo = Artista.objects.create(
            name="New Artist",
            image="http://example.com/new_artist.jpg"
        )
        album_nuevo = Album.objects.create(
            title="New Album",
            tags="rock",
            releaseDate=date(2023, 1, 1),
            length=3000,
            cover="http://example.com/new.jpg",
            playcount=15000,
            autor=artista_nuevo
        )
        mock_persistir.return_value = (artista_nuevo, album_nuevo)
        
        self.client.force_authenticate(user=self.user)
        #aca se hace el follow
        response = self.client.get("/api/v1/follow/New%20Artist/New%20Album")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "Followed successfully")
        
        #verificamos que el follow exista
        follow_exists = Follow.objects.filter(usuario=self.user, album=album_nuevo).exists()
        self.assertTrue(follow_exists)

        #nos fijamos q se haya logueado y notificado bien
        mock_log.assert_called_once_with("el usuario testuser siguió el album New Album")
        mock_notif.assert_called_once_with(self.user, "Seguido con éxito", f"Has seguido con éxito el album New Album de New Artist")

    @patch("albums.views.logAction")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    def test_remove_album_from_follow_list(
        self, mock_buscar_album, mock_persistir, mock_log_action
    ):
        Follow.objects.create(usuario=self.user, album=self.album1)
        
        mock_album_data = {
            "titulo": self.album1.title,
            "artista": self.artista.name,
            "foto": self.album1.cover,
            "fechaLanzamiento": "01 Jan 2020",
            "duracion": self.album1.length,
            "reproducciones": self.album1.playcount,
            "etiquetas": self.album1.tags
        }
        mock_buscar_album.return_value = mock_album_data
        mock_persistir.return_value = (self.artista, self.album1)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/v1/unfollow/Test%20Artist/Test%20Album%201")
        
        #nos fijamos q este todo bien
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "Unfollowed successfully")
        
        # verificamos q se haya eliminado el follow
        follow_exists = Follow.objects.filter(usuario=self.user,album=self.album1).exists()
        self.assertFalse(follow_exists)
        mock_log_action.assert_called_once_with("el usuario testuser dejó de seguir el album Test Album 1")

class IntegrationTests(TestCase):
    #tests de integración teniendo en cuenta el ciclo de seguir y dejar de seguir un album
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    @patch("albums.views.logAction")
    @patch("albums.views.crearNotificacion")
    @patch("albums.views.persistirAlbum")
    @patch("albums.views.api.buscarAlbum")
    def test_cycle_follow_and_unfollow(
        self, mock_buscar_album, mock_persistir, mock_notif, mock_log_action
    ):
        #los ponemos como variables aca porq lo vamos a usar seguido
        album_title = "Integration Album"
        artist_name = "Integration Artist"
        
        #mockeamos lo q devolveria la api
        mock_album_data = {
            "titulo": album_title,
            "artista": artist_name,
            "foto": "http://example.com/cover.jpg",
            "fechaLanzamiento": "01 Jan 2023",
            "duracion": 3000,
            "reproducciones": 100,
            "etiquetas": "test"
        }
        mock_buscar_album.return_value = mock_album_data

        artist_obj = Artista.objects.create(name=artist_name, image="img.jpg")
        album_obj = Album.objects.create(title=album_title, autor=artist_obj)
        
        mock_persistir.return_value = (artist_obj, album_obj)

        self.client.force_authenticate(user=self.user)

        #comenzamos con el ciclo: usuario sigue al album
        response_follow = self.client.get("/api/v1/follow/Integration%20Artist/Integration%20Album")      
        self.assertEqual(response_follow.status_code, status.HTTP_200_OK)
        
        #verificamos q el Follow existe en la db
        self.assertTrue(Follow.objects.filter(usuario=self.user, album=album_obj).exists())

        #verificamos los logs y las notifs de esto
        mock_log_action.assert_called_once_with(f"el usuario testuser siguió el album {album_title}")
        mock_notif.assert_called_once_with(self.user, "Seguido con éxito", f"Has seguido con éxito el album {album_title} de {artist_name}")

        #reseteamos los mocks
        mock_log_action.reset_mock()
        mock_notif.reset_mock() 

        #seguimos con el ciclo: usuario dejar de seguir
        response_unfollow = self.client.get("/api/v1/unfollow/Integration%20Artist/Integration%20Album")
       
        self.assertEqual(response_unfollow.status_code, status.HTTP_200_OK)

        #verificamos q el follow no exista
        self.assertFalse(Follow.objects.filter(usuario=self.user, album=album_obj).exists())

        #verificamos q el album y el artista si siguen existiendo
        self.assertTrue(Album.objects.filter(id=album_obj.id).exists())
        self.assertTrue(Artista.objects.filter(id=artist_obj.id).exists())

        #verificamos los logs y las notifs del unfollow
        mock_log_action.assert_called_once_with(f"el usuario testuser dejó de seguir el album {album_title}")
        mock_notif.assert_not_called()

