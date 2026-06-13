from django.contrib import admin
from .models import AttendanceAlert, PeriodAttendance, StudentAttendance, TeacherAttendance


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "marking_method", "marked_by")
    list_filter = ("status", "date", "marking_method", "class_obj")
    search_fields = ("student__student_id", "student__user__first_name")
    date_hierarchy = "date"


@admin.register(PeriodAttendance)
class PeriodAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "class_subject", "date", "period_number", "status")
    list_filter = ("status", "date")


@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ("teacher", "date", "status", "check_in_time", "check_out_time")
    list_filter = ("status", "date")
    date_hierarchy = "date"


@admin.register(AttendanceAlert)
class AttendanceAlertAdmin(admin.ModelAdmin):
    list_display = ("student", "alert_type", "is_resolved", "created_at")
    list_filter = ("alert_type", "is_resolved")
