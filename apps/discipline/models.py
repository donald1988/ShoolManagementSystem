from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class BehaviorCategory(TimeStampedModel):
    SEVERITY_CHOICES = [
        ("minor", "Minor"),
        ("moderate", "Moderate"),
        ("major", "Major"),
        ("severe", "Severe"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="behavior_categories")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity_level = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    points_deducted = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "behavior_categories"
        verbose_name_plural = "Behavior Categories"

    def __str__(self):
        return f"{self.name} ({self.get_severity_level_display()})"


class DisciplineIncident(TimeStampedModel):
    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    ACTION_CHOICES = [
        ("warning", "Warning"),
        ("detention", "Detention"),
        ("suspension", "Suspension"),
        ("expulsion", "Expulsion"),
        ("counseling", "Counseling"),
        ("parent_meeting", "Parent Meeting"),
        ("community_service", "Community Service"),
        ("other", "Other"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="discipline_incidents")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="discipline_incidents")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reported_discipline_incidents"
    )
    category = models.ForeignKey(BehaviorCategory, on_delete=models.SET_NULL, null=True, related_name="incidents")
    incident_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    witnesses = models.TextField(blank=True)
    evidence = models.FileField(upload_to="discipline/evidence/", blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="reported")
    action_taken = models.CharField(max_length=20, choices=ACTION_CHOICES, blank=True)
    action_details = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="resolved_discipline_incidents",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    parent_notified = models.BooleanField(default=False)
    parent_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "discipline_incidents"

    def __str__(self):
        return f"Incident - {self.student} on {self.incident_date}"


class Detention(TimeStampedModel):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("attended", "Attended"),
        ("missed", "Missed"),
        ("cancelled", "Cancelled"),
    ]

    incident = models.ForeignKey(
        DisciplineIncident, on_delete=models.SET_NULL, null=True, blank=True, related_name="detentions"
    )
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="detentions")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    supervised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="supervised_detentions"
    )
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="scheduled")
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "detentions"

    def __str__(self):
        return f"Detention - {self.student} on {self.date}"


class Suspension(TimeStampedModel):
    TYPE_CHOICES = [
        ("in_school", "In-School"),
        ("out_of_school", "Out of School"),
    ]

    incident = models.ForeignKey(
        DisciplineIncident, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspensions"
    )
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="suspensions")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    suspension_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="approved_suspensions"
    )
    conditions_for_return = models.TextField(blank=True)
    parent_acknowledged = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "suspensions"

    def __str__(self):
        return f"Suspension - {self.student} ({self.start_date} to {self.end_date})"


class BehaviorPoints(TimeStampedModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="behavior_points")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="behavior_points")
    total_points = models.IntegerField(default=0)
    positive_points = models.PositiveIntegerField(default=0)
    negative_points = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "behavior_points"
        unique_together = ("student", "academic_year")
        verbose_name_plural = "Behavior Points"

    def __str__(self):
        return f"Points - {self.student} ({self.total_points})"
