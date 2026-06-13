from django.contrib import admin

from .models import HealthIncident, HealthVisit, MedicalRecord, Vaccination


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "blood_group", "insurance_provider", "last_physical_date")
    search_fields = ("student__student_id", "student__user__first_name")


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ("student", "vaccine_name", "dose_number", "administered_date", "next_due_date")
    list_filter = ("vaccine_name", "administered_date")
    search_fields = ("student__student_id", "vaccine_name")


@admin.register(HealthVisit)
class HealthVisitAdmin(admin.ModelAdmin):
    list_display = ("student", "visit_date", "reason", "follow_up_required", "parent_notified")
    list_filter = ("follow_up_required", "parent_notified")
    search_fields = ("student__student_id", "reason")
    date_hierarchy = "visit_date"


@admin.register(HealthIncident)
class HealthIncidentAdmin(admin.ModelAdmin):
    list_display = ("school", "incident_type", "severity", "incident_date", "parent_contacted")
    list_filter = ("incident_type", "severity", "parent_contacted")
    date_hierarchy = "incident_date"
