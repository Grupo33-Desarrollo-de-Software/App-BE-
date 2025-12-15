from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from notificaciones.models import Notificacion

User = get_user_model()


class HomeNotificationTests(TestCase):
    # clase para testear:  mostrar notificaciones en pantalla principal
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="homeuser", password="testpass123", email="u@test.com"
        )

    def test_index_shows_pending_notifications(self):
        notif = Notificacion.objects.create(
            titulo="Aviso", cuerpo="Contenido", usuario=self.user
        )

        self.client.force_login(self.user)
        resp = self.client.get("/home/")
        self.assertEqual(resp.status_code, 200)
        # Convierte el texto a bytes para poder usarlo en el assert
        self.assertIn(b"Aviso", resp.content)
        self.assertIn(b"Contenido", resp.content)
