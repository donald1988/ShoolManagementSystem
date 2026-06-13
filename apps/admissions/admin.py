from django.contrib import admin
from .models import AdmissionApplication, AdmissionDocument, AdmissionPeriod, SeatAllocation


@admin.register(AdmissionPeriod)
class AdmissionPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "academic_year", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "school")


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ("application_number", "first_name", "last_name", "status", "applying_for_class", "created_at")
    list_filter = ("status", "school")
    search_fields = ("application_number", "first_name", "last_name", "email")


@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "document_type")


@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "admission_period", "total_seats", "filled_seats", "available_seats")
