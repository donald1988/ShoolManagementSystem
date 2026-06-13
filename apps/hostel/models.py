from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Building(TimeStampedModel):
    """Hostel building."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="hostel_buildings")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    warden = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="warden_buildings"
    )
    total_rooms = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hostel_buildings"

    def __str__(self):
        return self.name


class Floor(TimeStampedModel):
    """Floor within a hostel building."""

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="floors")
    name = models.CharField(max_length=100)
    floor_number = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "hostel_floors"
        ordering = ["floor_number"]

    def __str__(self):
        return f"{self.building.name} - {self.name}"


class Room(TimeStampedModel):
    """Hostel room."""

    ROOM_TYPE_CHOICES = [
        ("single", "Single"),
        ("double", "Double"),
        ("dormitory", "Dormitory"),
    ]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=15, choices=ROOM_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    occupied = models.PositiveIntegerField(default=0)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    has_ac = models.BooleanField(default=False)
    has_bathroom = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hostel_rooms"
        unique_together = [("floor", "room_number")]

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"


class Bed(TimeStampedModel):
    """Individual bed in a hostel room."""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="beds")
    bed_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)
    student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="hostel_beds"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "hostel_beds"

    def __str__(self):
        return f"{self.room.room_number} - Bed {self.bed_number}"


class HostelAllocation(TimeStampedModel):
    """Student hostel room allocation record."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="hostel_allocations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="allocations")
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True, related_name="allocations")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="hostel_allocations")
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="hostel_allocations_made"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "hostel_allocations"

    def __str__(self):
        return f"{self.student} - Room {self.room.room_number}"
