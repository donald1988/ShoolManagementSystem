from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"students", views.StudentViewSet, basename="student")
router.register(r"parents", views.ParentViewSet, basename="parent")
router.register(r"student-parents", views.StudentParentViewSet, basename="student-parent")
router.register(r"emergency-contacts", views.EmergencyContactViewSet, basename="emergency-contact")
router.register(r"documents", views.StudentDocumentViewSet, basename="student-document")
router.register(r"promotions", views.StudentPromotionViewSet, basename="student-promotion")

urlpatterns = [
    path("", include(router.urls)),
]
