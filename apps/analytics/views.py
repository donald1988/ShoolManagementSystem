from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsPrincipal, IsSuperAdmin

from .models import AIPrediction, DashboardWidget, Report, ReportExecution
from .serializers import (
    AIPredictionSerializer,
    DashboardWidgetSerializer,
    ReportExecutionSerializer,
    ReportSerializer,
)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsPrincipal]
    filterset_fields = ["school", "widget_type", "is_active", "role"]

    def get_queryset(self):
        qs = DashboardWidget.objects.select_related("school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Return all active widgets for the current user's role."""
        user = request.user
        qs = self.get_queryset().filter(is_active=True, role=user.role)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["school", "report_type", "is_public"]

    def get_queryset(self):
        qs = Report.objects.select_related("created_by", "school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """Execute a report and create an execution record."""
        report = self.get_object()
        execution = ReportExecution.objects.create(
            report=report,
            executed_by=request.user,
            parameters_used=request.data.get("parameters", {}),
            status="pending",
        )
        return Response(
            ReportExecutionSerializer(execution).data,
            status=status.HTTP_201_CREATED,
        )


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportExecutionSerializer
    permission_classes = [IsPrincipal]
    filterset_fields = ["report", "status"]

    def get_queryset(self):
        qs = ReportExecution.objects.select_related("report", "executed_by")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(report__school_id=user.school_id)
        return qs


class AIPredictionViewSet(viewsets.ModelViewSet):
    serializer_class = AIPredictionSerializer
    permission_classes = [IsPrincipal]
    filterset_fields = ["school", "prediction_type", "student", "is_reviewed"]

    def get_queryset(self):
        qs = AIPrediction.objects.select_related("student__user", "reviewed_by", "school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs
