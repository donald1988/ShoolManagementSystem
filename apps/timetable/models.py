from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Period(TimeStampedModel):
    """Time period/slot in the school day."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveSmallIntegerField()
    is_break = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "periods"
        unique_together = [("school", "order")]
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Room(TimeStampedModel):
    """Physical room/space in the school."""

    ROOM_TYPES = [
        ("classroom", "Classroom"),
        ("lab", "Laboratory"),
        ("auditorium", "Auditorium"),
        ("library", "Library"),
        ("sports", "Sports"),
        ("other", "Other"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    building = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=40)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="classroom")
    is_available = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "rooms"
        unique_together = [("school", "code")]

    def __str__(self):
        return f"{self.name} ({self.code})"


class TimetableEntry(TimeStampedModel):
    """A single timetable slot assignment."""

    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="timetable_entries")
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE, related_name="timetable_entries"
    )
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="timetable_entries")
    section = models.ForeignKey(
        "academics.Section", on_delete=models.CASCADE, null=True, blank=True, related_name="timetable_entries"
    )
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="timetable_entries")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timetable_entries"
    )
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="timetable_entries")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name="timetable_entries")
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "timetable_entries"
        unique_together = [("class_obj", "section", "period", "day_of_week", "academic_year")]

    def __str__(self):
        return f"{self.class_obj} - {self.subject} - {self.day_of_week} {self.period.name}"


class TimetableChange(TimeStampedModel):
    """Temporary change/substitution in the timetable."""

    original_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name="changes")
    date = models.DateField()
    substitute_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="substitution_changes"
    )
    substitute_subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="substitution_changes"
    )
    substitute_room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="substitution_changes"
    )
    reason = models.TextField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timetable_changes_made"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "timetable_changes"

    def __str__(self):
        return f"Change for {self.original_entry} on {self.date}"
