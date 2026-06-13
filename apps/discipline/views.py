from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, IsTeacher

from .models import BehaviorCategory, BehaviorPoints, Detention, DisciplineIncident, Suspension
from .serializers import (
    BehaviorCategorySerializer,
    BehaviorPointsSerializer,
    DetentionSerializer,
    DisciplineIncidentSerializer,
    SuspensionSerializer,
)


class BehaviorCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorCategorySerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "severity_level"]

    def get_queryset(self):
        qs = BehaviorCategory.objects.all()
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs


class DisciplineIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = DisciplineIncidentSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "student", "category", "status", "action_taken"]

    def get_queryset(self):
        qs = DisciplineIncident.objects.select_related(
            "student__user", "reported_by", "category", "resolved_by", "school"
        )
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsSchoolAdmin])
    def resolve(self, request, pk=None):
        incident = self.get_object()
        incident.status = "resolved"
        incident.resolved_by = request.user
        incident.resolved_at = timezone.now()
        incident.action_taken = request.data.get("action_taken", "")
        incident.action_details = request.data.get("action_details", "")
        incident.save()
        return Response(DisciplineIncidentSerializer(incident).data)


class DetentionViewSet(viewsets.ModelViewSet):
    serializer_class = DetentionSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "date", "status"]

    def get_queryset(self):
        qs = Detention.objects.select_related("student__user", "supervised_by", "incident")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs


class SuspensionViewSet(viewsets.ModelViewSet):
    serializer_class = SuspensionSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["student", "suspension_type"]

    def get_queryset(self):
        qs = Suspension.objects.select_related("student__user", "approved_by", "incident")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(approved_by=self.request.user)


class BehaviorPointsViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorPointsSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "academic_year"]

    def get_queryset(self):
        qs = BehaviorPoints.objects.select_related("student__user", "academic_year")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs
