from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsHR, IsSchoolAdmin, ReadOnly

from .models import (
    Employee,
    EmployeeContract,
    JobApplication,
    LeaveRequest,
    LeaveType,
    PerformanceReview,
    Recruitment,
)
from .serializers import (
    EmployeeContractSerializer,
    EmployeeSerializer,
    JobApplicationSerializer,
    LeaveRequestSerializer,
    LeaveTypeSerializer,
    PerformanceReviewSerializer,
    RecruitmentSerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsHR | ReadOnly]
    filterset_fields = ["school", "department", "contract_type", "is_active"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "designation"]

    def get_queryset(self):
        qs = Employee.objects.select_related("user", "school", "department", "salary")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class EmployeeContractViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeContractSerializer
    permission_classes = [IsHR]
    filterset_fields = ["employee", "contract_type", "is_active"]

    def get_queryset(self):
        return EmployeeContract.objects.select_related("employee__user")


class LeaveTypeViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHR | ReadOnly]
    filterset_fields = ["school", "is_paid", "is_active"]

    def get_queryset(self):
        qs = LeaveType.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["employee", "leave_type", "status"]
    search_fields = ["employee__first_name", "employee__last_name"]

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related("employee", "leave_type", "approved_by")
        if self.request.user.role in ("super_admin", "school_admin", "hr"):
            return qs
        return qs.filter(employee=self.request.user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsHR])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "approved"
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.remarks = request.data.get("remarks", "")
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=["post"], permission_classes=[IsHR])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "rejected"
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.remarks = request.data.get("remarks", "")
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsHR | ReadOnly]
    filterset_fields = ["employee", "reviewer", "academic_year", "status"]

    def get_queryset(self):
        qs = PerformanceReview.objects.select_related("employee", "reviewer", "academic_year")
        if self.request.user.role in ("super_admin", "school_admin", "hr"):
            return qs
        return qs.filter(employee=self.request.user)


class RecruitmentViewSet(viewsets.ModelViewSet):
    serializer_class = RecruitmentSerializer
    permission_classes = [IsHR | ReadOnly]
    filterset_fields = ["school", "department", "status"]
    search_fields = ["position", "description"]

    def get_queryset(self):
        qs = Recruitment.objects.select_related("school", "department", "posted_by").prefetch_related(
            "applications"
        )
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsHR]
    filterset_fields = ["recruitment", "status"]
    search_fields = ["applicant_name", "email"]

    def get_queryset(self):
        return JobApplication.objects.select_related("recruitment")
