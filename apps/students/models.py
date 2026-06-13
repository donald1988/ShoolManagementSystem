from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Student(TimeStampedModel):
    """Student profile linked to a user account."""

    STATUS_CHOICES = [
        ("new_admission", "New Admission"),
        ("enrolled", "Enrolled"),
        ("promoted", "Promoted"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
        ("withdrawn", "Withdrawn"),
        ("suspended", "Suspended"),
        ("alumni", "Alumni"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="students")
    student_id = models.CharField(max_length=30, unique=True, db_index=True)
    admission_number = models.CharField(max_length=30, blank=True, db_index=True)
    admission_date = models.DateField(null=True, blank=True)

    # Personal info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    religion = models.CharField(max_length=50, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Academic
    current_class = models.ForeignKey(
        "academics.Class", on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    current_section = models.ForeignKey(
        "academics.Section", on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    roll_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new_admission")

    # Medical
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)

    # Transport
    bus_route = models.ForeignKey(
        "transport.BusRoute", on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    pickup_point = models.CharField(max_length=255, blank=True)

    # Hostel
    hostel_room = models.ForeignKey(
        "hostel.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )

    photo = models.ImageField(upload_to="students/photos/", blank=True)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "students"

    def __str__(self):
        return f"{self.student_id} - {self.user.full_name}"


class Parent(TimeStampedModel):
    """Parent/guardian profile."""

    RELATIONSHIP_CHOICES = [
        ("father", "Father"),
        ("mother", "Mother"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parent_profile")
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="parents")
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=100, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "parents"

    def __str__(self):
        return self.user.full_name


class StudentParent(TimeStampedModel):
    """Links students to parents with relationship type."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_links")
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="student_links")
    relationship = models.CharField(
        max_length=20,
        choices=Parent.RELATIONSHIP_CHOICES,
        default="guardian",
    )
    is_primary_contact = models.BooleanField(default=False)
    is_emergency_contact = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_parents"
        unique_together = [("student", "parent")]

    def __str__(self):
        return f"{self.parent.user.full_name} → {self.student.user.full_name}"


class EmergencyContact(TimeStampedModel):
    """Emergency contacts for a student."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "emergency_contacts"

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class StudentDocument(TimeStampedModel):
    """Documents uploaded for a student."""

    DOCUMENT_TYPES = [
        ("birth_certificate", "Birth Certificate"),
        ("passport", "Passport"),
        ("id_card", "ID Card"),
        ("report_card", "Report Card"),
        ("medical_record", "Medical Record"),
        ("transfer_certificate", "Transfer Certificate"),
        ("photo", "Photo"),
        ("other", "Other"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="students/documents/")
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_documents"
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_documents"

    def __str__(self):
        return f"{self.title} ({self.document_type})"


class StudentPromotion(TimeStampedModel):
    """Track student promotions between classes."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="promotions")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE)
    from_class = models.ForeignKey(
        "academics.Class", on_delete=models.CASCADE, related_name="promotions_from"
    )
    to_class = models.ForeignKey(
        "academics.Class", on_delete=models.CASCADE, related_name="promotions_to"
    )
    from_section = models.ForeignKey(
        "academics.Section", on_delete=models.SET_NULL, null=True, blank=True, related_name="promotions_from"
    )
    to_section = models.ForeignKey(
        "academics.Section", on_delete=models.SET_NULL, null=True, blank=True, related_name="promotions_to"
    )
    promoted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_promotions"

    def __str__(self):
        return f"{self.student} → {self.to_class}"
