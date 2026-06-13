import csv

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.core.permissions import IsSuperAdmin

from .models import AuditLog, DataExportLog, LoginAttempt
from .serializers import AuditLogSerializer, DataExportLogSerializer, LoginAttemptSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["user", "school", "action", "model_name"]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user", "school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        """Export audit logs as CSV."""
        qs = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(["Timestamp", "User", "Action", "Model", "Object ID", "Object", "IP Address"])
        for log in qs.iterator():
            writer.writerow([
                log.timestamp,
                str(log.user) if log.user else "",
                log.action,
                log.model_name,
                log.object_id,
                log.object_repr,
                log.ip_address or "",
            ])
        return response


class LoginAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoginAttemptSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["email", "success"]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        return LoginAttempt.objects.all()


class DataExportLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DataExportLogSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["user", "school", "export_type", "model_name"]

    def get_queryset(self):
        qs = DataExportLog.objects.select_related("user", "school")
        user = self.request.user
        if user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs
