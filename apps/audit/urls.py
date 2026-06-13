from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"logs", views.AuditLogViewSet, basename="audit-log")
router.register(r"login-attempts", views.LoginAttemptViewSet, basename="login-attempt")
router.register(r"exports", views.DataExportLogViewSet, basename="data-export-log")

urlpatterns = [
    path("", include(router.urls)),
]
