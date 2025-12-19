from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from logger.models import Log

User = get_user_model()

class LoggerApiTests(TestCase):
    # clase para testear: generación de bitacora y panel de monitoreo
    def setUp(self):
        self.client = APIClient()
        #crea un usuario administrador para los tests
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass123",
            email="admin@test.com",
            is_staff=True,  #necesario para IsAdminUser
            is_superuser=True
        )

    def test_api_monitor_panel_returns_logs(self):
        # verifica que se devuelvan los logs
        Log.objects.create(logtype="CRUD", body="entry 1")
        Log.objects.create(logtype="ERROR", body="entry 2")

        #autentica al usuario administrador antes de hacer la petición
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get("/api/v1/logger/logs/ANY")

        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 2)

    def test_monitor_log_generation_records_response_time(self):
        # verifica que se cree un log de tipo RESPONSETIME al hacer un get a la api
        initial = Log.objects.count()

        #autentica al usuario administrador antes de hacer la petición
        self.client.force_authenticate(user=self.admin_user)
        self.client.get("/api/v1/logger/logs/ANY")

        self.assertEqual(Log.objects.count(), initial + 1)
        self.assertEqual(Log.objects.last().logtype, "RESPONSETIME")
