from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"drivers", views.DriverViewSet, basename="driver")
router.register(r"routes", views.BusRouteViewSet, basename="bus-route")
router.register(r"stops", views.BusStopViewSet, basename="bus-stop")
router.register(r"student-transport", views.StudentTransportViewSet, basename="student-transport")
router.register(r"gps-tracking", views.GPSTrackingViewSet, basename="gps-tracking")

urlpatterns = [
    path("", include(router.urls)),
]
