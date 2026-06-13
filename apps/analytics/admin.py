from django.contrib import admin

from .models import AIPrediction, DashboardWidget, Report, ReportExecution


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "widget_type", "position", "is_active", "role")
    list_filter = ("widget_type", "is_active", "role")
    search_fields = ("title",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "report_type", "created_by", "is_public")
    list_filter = ("report_type", "is_public")
    search_fields = ("name",)


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ("report", "executed_by", "executed_at", "status", "row_count", "execution_time_ms")
    list_filter = ("status",)
    date_hierarchy = "executed_at"


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "prediction_type", "prediction_date", "risk_score", "confidence", "is_reviewed")
    list_filter = ("prediction_type", "is_reviewed")
    search_fields = ("student__student_id",)
