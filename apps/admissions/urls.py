from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"periods", views.AdmissionPeriodViewSet, basename="admission-period")
router.register(r"applications", views.AdmissionApplicationViewSet, basename="admission-application")
router.register(r"documents", views.AdmissionDocumentViewSet, basename="admission-document")
router.register(r"seats", views.SeatAllocationViewSet, basename="seat-allocation")

urlpatterns = [
    path("", include(router.urls)),
]
