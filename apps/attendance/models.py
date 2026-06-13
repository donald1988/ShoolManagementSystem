from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class StudentAttendance(TimeStampedModel):
    """Daily student attendance record."""

    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
        ("half_day", "Half Day"),
    ]

    MARKING_METHOD_CHOICES = [
        ("manual", "Manual"),
        ("qr", "QR Code"),
        ("rfid", "RFID"),
        ("biometric", "Biometric"),
        ("app", "Mobile App"),
    ]

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_records")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="attendance_records")
    section = models.ForeignKey(
        "academics.Section", on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_records"
    )
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="present")
    marking_method = models.CharField(max_length=15, choices=MARKING_METHOD_CHOICES, default="manual")
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="attendance_marked"
    )
    remarks = models.TextField(blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_attendance"
        unique_together = [("student", "date")]

    def __str__(self):
        return f"{self.student} - {self.date}: {self.status}"


class PeriodAttendance(TimeStampedModel):
    """Period-wise attendance for each subject."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="period_attendance")
    class_subject = models.ForeignKey("academics.ClassSubject", on_delete=models.CASCADE, related_name="period_attendance")
    date = models.DateField(db_index=True)
    period_number = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=10,
        choices=StudentAttendance.STATUS_CHOICES,
        default="present",
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="period_attendance_marked"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "period_attendance"
        unique_together = [("student", "class_subject", "date", "period_number")]

    def __str__(self):
        return f"{self.student} - {self.class_subject} P{self.period_number}: {self.status}"


class TeacherAttendance(TimeStampedModel):
    """Teacher daily attendance."""

    teacher = models.ForeignKey("academics.Teacher", on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("on_leave", "On Leave"),
            ("half_day", "Half Day"),
        ],
        default="present",
    )
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "teacher_attendance"
        unique_together = [("teacher", "date")]

    def __str__(self):
        return f"{self.teacher} - {self.date}: {self.status}"


class AttendanceAlert(TimeStampedModel):
    """Alerts for chronic absenteeism."""

    ALERT_TYPES = [
        ("absent_streak", "Absent Streak"),
        ("low_percentage", "Low Attendance Percentage"),
        ("chronic_absent", "Chronic Absenteeism"),
    ]

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_alerts")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_alerts"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "attendance_alerts"

    def __str__(self):
        return f"{self.alert_type} - {self.student}"
