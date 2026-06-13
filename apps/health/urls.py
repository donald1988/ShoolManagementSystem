from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"medical-records", views.MedicalRecordViewSet, basename="medical-record")
router.register(r"vaccinations", views.VaccinationViewSet, basename="vaccination")
router.register(r"visits", views.HealthVisitViewSet, basename="health-visit")
router.register(r"incidents", views.HealthIncidentViewSet, basename="health-incident")

urlpatterns = [
    path("", include(router.urls)),
]
