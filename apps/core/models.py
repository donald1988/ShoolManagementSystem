import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with UUID primary key and timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class School(TimeStampedModel):
    """Top-level school/institution entity for multi-tenant support."""

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    logo = models.ImageField(upload_to="schools/logos/", blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="US")
    postal_code = models.CharField(max_length=20)
    timezone = models.CharField(max_length=50, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
    subscription_plan = models.CharField(
        max_length=20,
        choices=[
            ("free", "Free"),
            ("basic", "Basic"),
            ("pro", "Professional"),
            ("enterprise", "Enterprise"),
        ],
        default="free",
    )
    subscription_expires = models.DateField(null=True, blank=True)
    max_students = models.PositiveIntegerField(default=100)
    max_staff = models.PositiveIntegerField(default=20)

    class Meta(TimeStampedModel.Meta):
        db_table = "schools"

    def __str__(self):
        return self.name


class Campus(TimeStampedModel):
    """Physical campus/branch of a school."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="campuses")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="US")
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "campuses"
        unique_together = [("school", "code")]
        verbose_name_plural = "Campuses"

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class AcademicYear(TimeStampedModel):
    """Academic year definition."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=50)  # e.g., "2025-2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "academic_years"
        unique_together = [("school", "name")]

    def __str__(self):
        return f"{self.school.name} - {self.name}"

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(school=self.school, is_current=True).exclude(pk=self.pk).update(
                is_current=False
            )
        super().save(*args, **kwargs)


class Term(TimeStampedModel):
    """Terms/semesters within an academic year."""

    TERM_TYPES = [
        ("semester", "Semester"),
        ("trimester", "Trimester"),
        ("quarter", "Quarter"),
        ("term", "Term"),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=50)
    term_type = models.CharField(max_length=20, choices=TERM_TYPES, default="semester")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta(TimeStampedModel.Meta):
        db_table = "terms"
        unique_together = [("academic_year", "name")]
        ordering = ["order"]

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"


class SystemConfiguration(TimeStampedModel):
    """System-wide configuration key-value store."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="configurations")
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "system_configurations"
        unique_together = [("school", "key")]

    def __str__(self):
        return f"{self.key}: {self.value}"
