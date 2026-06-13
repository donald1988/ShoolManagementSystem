from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AcademicYear, Campus, School, SystemConfiguration, Term
from .permissions import IsSchoolAdmin, IsSuperAdmin
from .serializers import (
    AcademicYearSerializer,
    CampusSerializer,
    SchoolSerializer,
    SystemConfigurationSerializer,
    TermSerializer,
)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["is_active", "subscription_plan", "country"]
    search_fields = ["name", "code", "city"]

    def get_permissions(self):
        if self.action in ("retrieve", "list"):
            return [IsSchoolAdmin()]
        return super().get_permissions()


class CampusViewSet(viewsets.ModelViewSet):
    serializer_class = CampusSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_active", "is_main"]
    search_fields = ["name", "code", "city"]

    def get_queryset(self):
        qs = Campus.objects.select_related("school")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class AcademicYearViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicYearSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_current"]

    def get_queryset(self):
        qs = AcademicYear.objects.prefetch_related("terms")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=True, methods=["post"])
    def set_current(self, request, pk=None):
        academic_year = self.get_object()
        academic_year.is_current = True
        academic_year.save()
        return Response({"status": "Academic year set as current"})


class TermViewSet(viewsets.ModelViewSet):
    serializer_class = TermSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["academic_year", "is_current", "term_type"]

    def get_queryset(self):
        qs = Term.objects.select_related("academic_year__school")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(academic_year__school_id=self.request.user.school_id)
        return qs


class SystemConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = SystemConfigurationSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["school"]
    search_fields = ["key", "description"]

    def get_queryset(self):
        qs = SystemConfiguration.objects.select_related("school")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs
