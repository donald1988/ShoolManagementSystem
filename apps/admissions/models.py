from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AdmissionPeriod(TimeStampedModel):
    """Defines an admission window."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="admission_periods")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="admission_periods")
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    max_applications = models.PositiveIntegerField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "admission_periods"

    def __str__(self):
        return f"{self.name} ({self.academic_year.name})"


class AdmissionApplication(TimeStampedModel):
    """Student admission application."""

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("interview_scheduled", "Interview Scheduled"),
        ("assessment_scheduled", "Assessment Scheduled"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("waitlisted", "Waitlisted"),
        ("fee_pending", "Fee Pending"),
        ("enrolled", "Enrolled"),
        ("withdrawn", "Withdrawn"),
    ]

    admission_period = models.ForeignKey(AdmissionPeriod, on_delete=models.CASCADE, related_name="applications")
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="admission_applications")
    application_number = models.CharField(max_length=30, unique=True, db_index=True)
    applying_for_class = models.ForeignKey(
        "academics.Class", on_delete=models.CASCADE, related_name="admission_applications"
    )

    # Applicant info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")])
    nationality = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    previous_school = models.CharField(max_length=255, blank=True)
    previous_class = models.CharField(max_length=50, blank=True)

    # Parent info
    parent_name = models.CharField(max_length=200)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20)
    parent_occupation = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="submitted")
    merit_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_notes = models.TextField(blank=True)
    assessment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_applications"
    )
    remarks = models.TextField(blank=True)
    student = models.OneToOneField(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_application"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "admission_applications"

    def __str__(self):
        return f"{self.application_number} - {self.first_name} {self.last_name}"


class AdmissionDocument(TimeStampedModel):
    """Documents submitted with an admission application."""

    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="admissions/documents/")
    document_type = models.CharField(max_length=50)

    class Meta(TimeStampedModel.Meta):
        db_table = "admission_documents"

    def __str__(self):
        return self.title


class SeatAllocation(TimeStampedModel):
    """Tracks available seats per class for an admission period."""

    admission_period = models.ForeignKey(AdmissionPeriod, on_delete=models.CASCADE, related_name="seat_allocations")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="seat_allocations")
    total_seats = models.PositiveIntegerField()
    filled_seats = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "seat_allocations"
        unique_together = [("admission_period", "class_obj")]

    @property
    def available_seats(self):
        return self.total_seats - self.filled_seats

    def __str__(self):
        return f"{self.class_obj.name}: {self.available_seats} available"
