from django.urls import path
from . import views

urlpatterns = [
    path("newlog", views.logview, name="newlog"),
    path("logs/<str:logtype>", views.getlogs, name="logs"),
    # Monitoring dashboard endpoints (admin-only)
    path("monitoring/dashboard", views.monitoring_dashboard, name="monitoring_dashboard"),
    path("monitoring/details/<uuid:request_id>", views.monitoring_details, name="monitoring_details"),
    path("monitoring/errors", views.monitoring_errors, name="monitoring_errors"),
]
