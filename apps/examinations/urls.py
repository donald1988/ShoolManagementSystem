from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"exam-types", views.ExamTypeViewSet, basename="exam-type")
router.register(r"exams", views.ExamViewSet, basename="exam")
router.register(r"schedules", views.ExamScheduleViewSet, basename="exam-schedule")
router.register(r"seating-plans", views.ExamSeatingPlanViewSet, basename="seating-plan")
router.register(r"grades", views.GradeViewSet, basename="grade")
router.register(r"grading-scales", views.GradingScaleViewSet, basename="grading-scale")
router.register(r"grade-ranges", views.GradeRangeViewSet, basename="grade-range")
router.register(r"report-cards", views.ReportCardViewSet, basename="report-card")

urlpatterns = [
    path("", include(router.urls)),
]
