from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"messages", views.MessageViewSet, basename="message")
router.register(r"announcements", views.AnnouncementViewSet, basename="announcement")
router.register(r"notification-templates", views.NotificationTemplateViewSet, basename="notification-template")
router.register(r"notifications", views.NotificationViewSet, basename="notification")
router.register(r"emergency-alerts", views.EmergencyAlertViewSet, basename="emergency-alert")

urlpatterns = [
    path("", include(router.urls)),
]
