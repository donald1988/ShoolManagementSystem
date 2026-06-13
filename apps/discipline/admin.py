from django.contrib import admin

from .models import BehaviorCategory, BehaviorPoints, Detention, DisciplineIncident, Suspension


@admin.register(BehaviorCategory)
class BehaviorCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "severity_level", "points_deducted")
    list_filter = ("severity_level",)
    search_fields = ("name",)


@admin.register(DisciplineIncident)
class DisciplineIncidentAdmin(admin.ModelAdmin):
    list_display = ("student", "category", "status", "action_taken", "incident_date", "parent_notified")
    list_filter = ("status", "action_taken", "parent_notified")
    search_fields = ("student__student_id", "student__user__first_name", "description")
    date_hierarchy = "incident_date"


@admin.register(Detention)
class DetentionAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "start_time", "end_time", "status", "location")
    list_filter = ("status", "date")
    search_fields = ("student__student_id", "reason")
    date_hierarchy = "date"


@admin.register(Suspension)
class SuspensionAdmin(admin.ModelAdmin):
    list_display = ("student", "suspension_type", "start_date", "end_date", "parent_acknowledged")
    list_filter = ("suspension_type", "parent_acknowledged")
    search_fields = ("student__student_id",)


@admin.register(BehaviorPoints)
class BehaviorPointsAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "total_points", "positive_points", "negative_points")
    list_filter = ("academic_year",)
    search_fields = ("student__student_id",)
