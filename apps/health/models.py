from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class MedicalRecord(TimeStampedModel):
    student = models.OneToOneField("students.Student", on_delete=models.CASCADE, related_name="medical_record")
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    emergency_medical_info = models.TextField(blank=True)
    insurance_provider = models.CharField(max_length=255, blank=True)
    insurance_number = models.CharField(max_length=100, blank=True)
    last_physical_date = models.DateField(null=True, blank=True)
    doctor_name = models.CharField(max_length=255, blank=True)
    doctor_phone = models.CharField(max_length=20, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "medical_records"

    def __str__(self):
        return f"Medical Record - {self.student}"


class Vaccination(TimeStampedModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="vaccinations")
    vaccine_name = models.CharField(max_length=255)
    dose_number = models.PositiveSmallIntegerField(default=1)
    administered_date = models.DateField()
    administered_by = models.CharField(max_length=255, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "vaccinations"

    def __str__(self):
        return f"{self.vaccine_name} (Dose {self.dose_number}) - {self.student}"


class HealthVisit(TimeStampedModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_visits")
    visit_date = models.DateTimeField()
    reason = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medication_given = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    attended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="health_visits_attended"
    )
    parent_notified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "health_visits"

    def __str__(self):
        return f"Visit - {self.student} on {self.visit_date}"


class HealthIncident(TimeStampedModel):
    INCIDENT_TYPE_CHOICES = [
        ("injury", "Injury"),
        ("illness", "Illness"),
        ("allergy_reaction", "Allergy Reaction"),
        ("mental_health", "Mental Health"),
        ("other", "Other"),
    ]

    SEVERITY_CHOICES = [
        ("minor", "Minor"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
        ("critical", "Critical"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="health_incidents")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reported_health_incidents"
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, null=True, blank=True, related_name="health_incidents"
    )
    incident_date = models.DateTimeField()
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES)
    description = models.TextField()
    action_taken = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    parent_contacted = models.BooleanField(default=False)
    ambulance_called = models.BooleanField(default=False)
    hospital_visit = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "health_incidents"

    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.incident_date}"
