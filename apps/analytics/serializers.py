from rest_framework import serializers

from .models import AIPrediction, DashboardWidget, Report, ReportExecution


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by")


class ReportExecutionSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source="report.name", read_only=True)
    executed_by_name = serializers.CharField(source="executed_by.full_name", read_only=True)

    class Meta:
        model = ReportExecution
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "executed_by", "executed_at")


class AIPredictionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AIPrediction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
