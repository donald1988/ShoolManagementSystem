from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"employees", views.EmployeeViewSet, basename="employee")
router.register(r"contracts", views.EmployeeContractViewSet, basename="employee-contract")
router.register(r"leave-types", views.LeaveTypeViewSet, basename="leave-type")
router.register(r"leave-requests", views.LeaveRequestViewSet, basename="leave-request")
router.register(r"performance-reviews", views.PerformanceReviewViewSet, basename="performance-review")
router.register(r"recruitments", views.RecruitmentViewSet, basename="recruitment")
router.register(r"job-applications", views.JobApplicationViewSet, basename="job-application")

urlpatterns = [
    path("", include(router.urls)),
]
