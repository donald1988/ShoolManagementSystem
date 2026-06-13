from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"periods", views.PeriodViewSet, basename="period")
router.register(r"rooms", views.RoomViewSet, basename="room")
router.register(r"entries", views.TimetableEntryViewSet, basename="timetable-entry")
router.register(r"changes", views.TimetableChangeViewSet, basename="timetable-change")

urlpatterns = [
    path("", include(router.urls)),
]
