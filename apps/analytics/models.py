from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class DashboardWidget(TimeStampedModel):
    WIDGET_TYPE_CHOICES = [
        ("chart", "Chart"),
        ("table", "Table"),
        ("metric", "Metric"),
        ("list", "List"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="dashboard_widgets")
    title = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=10, choices=WIDGET_TYPE_CHOICES)
    data_source = models.CharField(max_length=255, help_text="API endpoint or query identifier")
    config = models.JSONField(default=dict, help_text="Chart type, colors, etc.")
    position = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=50, help_text="Which role sees this widget")

    class Meta(TimeStampedModel.Meta):
        db_table = "dashboard_widgets"
        ordering = ["position"]

    def __str__(self):
        return self.title


class Report(TimeStampedModel):
    REPORT_TYPE_CHOICES = [
        ("academic", "Academic"),
        ("financial", "Financial"),
        ("attendance", "Attendance"),
        ("hr", "HR"),
        ("custom", "Custom"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=15, choices=REPORT_TYPE_CHOICES)
    query = models.TextField(help_text="SQL or query parameters")
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_reports"
    )
    is_public = models.BooleanField(default=False)
    schedule = models.CharField(max_length=100, blank=True, help_text="Cron expression for scheduled reports")

    class Meta(TimeStampedModel.Meta):
        db_table = "reports"

    def __str__(self):
        return self.name


class ReportExecution(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="executions")
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="report_executions"
    )
    executed_at = models.DateTimeField(auto_now_add=True)
    parameters_used = models.JSONField(default=dict)
    result_file = models.FileField(upload_to="reports/results/", blank=True)
    row_count = models.PositiveIntegerField(null=True, blank=True)
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "report_executions"

    def __str__(self):
        return f"{self.report.name} - {self.executed_at}"


class AIPrediction(TimeStampedModel):
    PREDICTION_TYPE_CHOICES = [
        ("dropout_risk", "Dropout Risk"),
        ("performance", "Performance"),
        ("attendance", "Attendance"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="ai_predictions")
    prediction_type = models.CharField(max_length=15, choices=PREDICTION_TYPE_CHOICES)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="ai_predictions")
    prediction_date = models.DateField()
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    factors = models.JSONField(default=dict)
    recommendation = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_predictions"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "ai_predictions"

    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.student}"
