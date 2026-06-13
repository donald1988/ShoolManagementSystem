import uuid

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin

from .models import AdmissionApplication, AdmissionDocument, AdmissionPeriod, SeatAllocation
from .serializers import (
    AdmissionApplicationListSerializer,
    AdmissionApplicationSerializer,
    AdmissionDocumentSerializer,
    AdmissionPeriodSerializer,
    SeatAllocationSerializer,
)


class AdmissionPeriodViewSet(viewsets.ModelViewSet):
    serializer_class = AdmissionPeriodSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "academic_year", "is_active"]

    def get_queryset(self):
        qs = AdmissionPeriod.objects.select_related("school", "academic_year")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    filterset_fields = ["school", "admission_period", "status", "applying_for_class"]
    search_fields = ["application_number", "first_name", "last_name", "email"]
    ordering_fields = ["created_at", "merit_score"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsSchoolAdmin()]

    def get_serializer_class(self):
        if self.action == "list":
            return AdmissionApplicationListSerializer
        return AdmissionApplicationSerializer

    def get_queryset(self):
        qs = AdmissionApplication.objects.select_related("applying_for_class", "admission_period")
        if self.request.user.is_authenticated:
            if self.request.user.role != "super_admin" and self.request.user.school_id:
                qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    def perform_create(self, serializer):
        app_number = f"APP-{uuid.uuid4().hex[:8].upper()}"
        serializer.save(application_number=app_number)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        application = self.get_object()
        application.status = "approved"
        application.reviewed_by = request.user
        application.save(update_fields=["status", "reviewed_by"])
        return Response({"detail": "Application approved."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()
        application.status = "rejected"
        application.reviewed_by = request.user
        application.remarks = request.data.get("remarks", "")
        application.save(update_fields=["status", "reviewed_by", "remarks"])
        return Response({"detail": "Application rejected."})

    @action(detail=True, methods=["post"])
    def waitlist(self, request, pk=None):
        application = self.get_object()
        application.status = "waitlisted"
        application.save(update_fields=["status"])
        return Response({"detail": "Application waitlisted."})


class AdmissionDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = AdmissionDocumentSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["application"]

    def get_queryset(self):
        return AdmissionDocument.objects.select_related("application")


class SeatAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = SeatAllocationSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["admission_period"]

    def get_queryset(self):
        return SeatAllocation.objects.select_related("admission_period", "class_obj")
