from django.contrib import admin

from .models import (
    Employee,
    EmployeeContract,
    JobApplication,
    LeaveRequest,
    LeaveType,
    PerformanceReview,
    Recruitment,
)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "school", "department", "designation", "contract_type", "is_active")
    list_filter = ("school", "department", "contract_type", "is_active")
    search_fields = ("employee_id", "user__first_name", "user__last_name")


@admin.register(EmployeeContract)
class EmployeeContractAdmin(admin.ModelAdmin):
    list_display = ("employee", "contract_type", "start_date", "end_date", "is_active")
    list_filter = ("contract_type", "is_active")


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "max_days_per_year", "is_paid", "is_active")
    list_filter = ("school", "is_paid", "is_active")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "days", "status")
    list_filter = ("status", "leave_type")
    search_fields = ("employee__first_name", "employee__last_name")


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ("employee", "reviewer", "academic_year", "review_period", "rating", "status")
    list_filter = ("academic_year", "status")


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ("position", "school", "department", "num_positions", "application_deadline", "status")
    list_filter = ("school", "department", "status")
    search_fields = ("position",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant_name", "recruitment", "email", "status")
    list_filter = ("status", "recruitment")
    search_fields = ("applicant_name", "email")
