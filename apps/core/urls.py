from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"schools", views.SchoolViewSet)
router.register(r"campuses", views.CampusViewSet, basename="campus")
router.register(r"academic-years", views.AcademicYearViewSet, basename="academicyear")
router.register(r"terms", views.TermViewSet, basename="term")
router.register(r"configurations", views.SystemConfigurationViewSet, basename="configuration")

urlpatterns = [
    path("", include(router.urls)),
]
