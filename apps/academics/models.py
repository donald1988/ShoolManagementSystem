from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Department(TimeStampedModel):
    """Academic department."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="headed_departments"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "departments"
        unique_together = [("school", "code")]

    def __str__(self):
        return self.name


class Class(TimeStampedModel):
    """Grade level / class (e.g., Grade 1, Class 10)."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    numeric_level = models.PositiveSmallIntegerField(help_text="Numeric grade level for ordering")
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "classes"
        unique_together = [("school", "code")]
        verbose_name_plural = "Classes"
        ordering = ["numeric_level"]

    def __str__(self):
        return self.name


class Section(TimeStampedModel):
    """Section within a class (e.g., A, B, C)."""

    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=40)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="class_teacher_sections"
    )
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "sections"
        unique_together = [("class_obj", "name")]

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Subject(TimeStampedModel):
    """Subject/course definition."""

    SUBJECT_TYPES = [
        ("theory", "Theory"),
        ("practical", "Practical"),
        ("elective", "Elective"),
        ("language", "Language"),
        ("co_curricular", "Co-Curricular"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="subjects")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default="theory")
    credits = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "subjects"
        unique_together = [("school", "code")]

    def __str__(self):
        return f"{self.code} - {self.name}"


class SubjectPrerequisite(TimeStampedModel):
    """Prerequisites for a subject."""

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="prerequisites")
    prerequisite = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="prerequisite_for")

    class Meta(TimeStampedModel.Meta):
        db_table = "subject_prerequisites"
        unique_together = [("subject", "prerequisite")]


class ClassSubject(TimeStampedModel):
    """Links subjects to classes (curriculum mapping)."""

    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="class_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="class_subjects")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="class_subjects")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="taught_subjects"
    )
    periods_per_week = models.PositiveSmallIntegerField(default=5)

    class Meta(TimeStampedModel.Meta):
        db_table = "class_subjects"
        unique_together = [("class_obj", "subject", "academic_year")]

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"


class Teacher(TimeStampedModel):
    """Teacher profile linked to user account."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="teachers")
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="teachers")
    designation = models.CharField(max_length=100, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "teachers"

    def __str__(self):
        return f"{self.employee_id} - {self.user.full_name}"


class Enrollment(TimeStampedModel):
    """Student enrollment in a class for an academic year."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="enrollments")
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="enrollments")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollments")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="enrollments")
    roll_number = models.CharField(max_length=20, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "enrollments"
        unique_together = [("student", "academic_year")]

    def __str__(self):
        return f"{self.student} → {self.class_obj.name} ({self.academic_year.name})"
