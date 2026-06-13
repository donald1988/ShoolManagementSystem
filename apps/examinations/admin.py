from django.contrib import admin
from .models import Exam, ExamSchedule, ExamSeatingPlan, ExamType, Grade, GradeRange, GradingScale, ReportCard


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "weight_percentage", "is_active")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "academic_year", "term", "start_date", "end_date", "is_published")
    list_filter = ("exam_type", "is_published", "academic_year")


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("exam", "class_obj", "subject", "date", "start_time", "end_time", "max_marks")
    list_filter = ("exam", "class_obj", "date")


@admin.register(ExamSeatingPlan)
class ExamSeatingPlanAdmin(admin.ModelAdmin):
    list_display = ("exam_schedule", "student", "seat_number", "room")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "exam_schedule", "marks_obtained", "grade_letter", "is_passed")
    list_filter = ("exam_schedule__exam", "grade_letter")
    search_fields = ("student__student_id",)


@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "is_default")


@admin.register(GradeRange)
class GradeRangeAdmin(admin.ModelAdmin):
    list_display = ("grading_scale", "letter", "min_percentage", "max_percentage", "grade_point")


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "term", "percentage", "gpa", "rank", "is_published")
    list_filter = ("is_published", "academic_year", "term")
