from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"student", views.StudentAttendanceViewSet, basename="student-attendance")
router.register(r"period", views.PeriodAttendanceViewSet, basename="period-attendance")
router.register(r"teacher", views.TeacherAttendanceViewSet, basename="teacher-attendance")
router.register(r"alerts", views.AttendanceAlertViewSet, basename="attendance-alert")

urlpatterns = [
    path("", include(router.urls)),
]
