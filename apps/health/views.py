from rest_framework import viewsets

from apps.core.permissions import IsTeacher

from .models import HealthIncident, HealthVisit, MedicalRecord, Vaccination
from .serializers import (
    HealthIncidentSerializer,
    HealthVisitSerializer,
    MedicalRecordSerializer,
    VaccinationSerializer,
)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student"]

    def get_queryset(self):
        qs = MedicalRecord.objects.select_related("student__user")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs


class VaccinationViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "vaccine_name"]

    def get_queryset(self):
        qs = Vaccination.objects.select_related("student__user")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs


class HealthVisitViewSet(viewsets.ModelViewSet):
    serializer_class = HealthVisitSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "follow_up_required", "parent_notified"]

    def get_queryset(self):
        qs = HealthVisit.objects.select_related("student__user", "attended_by")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(attended_by=self.request.user)


class HealthIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = HealthIncidentSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "incident_type", "severity", "student"]

    def get_queryset(self):
        qs = HealthIncident.objects.select_related("reported_by", "student__user", "school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
