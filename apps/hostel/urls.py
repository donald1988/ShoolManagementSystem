from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"buildings", views.BuildingViewSet, basename="building")
router.register(r"floors", views.FloorViewSet, basename="floor")
router.register(r"rooms", views.RoomViewSet, basename="room")
router.register(r"beds", views.BedViewSet, basename="bed")
router.register(r"allocations", views.HostelAllocationViewSet, basename="hostel-allocation")

urlpatterns = [
    path("", include(router.urls)),
]
