from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ExamType(TimeStampedModel):
    """Types of examinations."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="exam_types")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "exam_types"
        unique_together = [("school", "name")]

    def __str__(self):
        return self.name


class Exam(TimeStampedModel):
    """Examination schedule."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="exams")
    term = models.ForeignKey("core.Term", on_delete=models.CASCADE, related_name="exams")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="exams")
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    instructions = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "exams"

    def __str__(self):
        return self.name


class ExamSchedule(TimeStampedModel):
    """Individual exam schedule per subject."""

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="exam_schedules")
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="exam_schedules")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=33)
    invigilator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="invigilated_exams"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "exam_schedules"

    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} ({self.date})"


class ExamSeatingPlan(TimeStampedModel):
    """Seating arrangement for exams."""

    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="seating_plans")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="exam_seats")
    seat_number = models.CharField(max_length=10)
    room = models.CharField(max_length=50)

    class Meta(TimeStampedModel.Meta):
        db_table = "exam_seating_plans"
        unique_together = [("exam_schedule", "student")]


class Grade(TimeStampedModel):
    """Student exam grades/marks."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="grades")
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="grades")
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="grades_given"
    )
    is_absent = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "grades"
        unique_together = [("student", "exam_schedule")]

    def __str__(self):
        return f"{self.student} - {self.exam_schedule.subject.name}: {self.marks_obtained}"

    @property
    def percentage(self):
        if self.exam_schedule.max_marks > 0:
            return round(float(self.marks_obtained) / float(self.exam_schedule.max_marks) * 100, 2)
        return 0

    @property
    def is_passed(self):
        return self.marks_obtained >= self.exam_schedule.passing_marks


class GradingScale(TimeStampedModel):
    """Grade letter mapping configuration."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="grading_scales")
    name = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "grading_scales"

    def __str__(self):
        return self.name


class GradeRange(TimeStampedModel):
    """Defines grade letter ranges within a grading scale."""

    grading_scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name="ranges")
    letter = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=50, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "grade_ranges"
        ordering = ["-min_percentage"]

    def __str__(self):
        return f"{self.letter}: {self.min_percentage}% - {self.max_percentage}%"


class ReportCard(TimeStampedModel):
    """Generated report cards."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="report_cards")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE)
    term = models.ForeignKey("core.Term", on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rank = models.PositiveIntegerField(null=True, blank=True)
    total_students = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    teacher_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    generated_file = models.FileField(upload_to="report_cards/", blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "report_cards"
        unique_together = [("student", "academic_year", "term")]

    def __str__(self):
        return f"Report Card: {self.student} - {self.term}"
