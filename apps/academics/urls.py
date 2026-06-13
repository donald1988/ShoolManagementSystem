from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"departments", views.DepartmentViewSet, basename="department")
router.register(r"classes", views.ClassViewSet, basename="class")
router.register(r"sections", views.SectionViewSet, basename="section")
router.register(r"subjects", views.SubjectViewSet, basename="subject")
router.register(r"class-subjects", views.ClassSubjectViewSet, basename="class-subject")
router.register(r"teachers", views.TeacherViewSet, basename="teacher")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")

urlpatterns = [
    path("", include(router.urls)),
]
