from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    """School transport vehicle."""

    VEHICLE_TYPE_CHOICES = [
        ("bus", "Bus"),
        ("van", "Van"),
        ("car", "Car"),
    ]

    FUEL_TYPE_CHOICES = [
        ("diesel", "Diesel"),
        ("petrol", "Petrol"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="vehicles")
    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES)
    insurance_expiry = models.DateField()
    registration_expiry = models.DateField()
    gps_device_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "vehicles"

    def __str__(self):
        return f"{self.vehicle_number} ({self.vehicle_type})"


class Driver(TimeStampedModel):
    """Driver assigned to school transport."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="drivers")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="driver_profile"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    license_expiry = models.DateField()
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to="transport/drivers/", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "drivers"

    def __str__(self):
        return self.name


class BusRoute(TimeStampedModel):
    """Bus route with stops."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="bus_routes")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    estimated_time_minutes = models.PositiveIntegerField()
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="routes")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="routes")
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "bus_routes"
        unique_together = [("school", "code")]

    def __str__(self):
        return f"{self.code} - {self.name}"


class BusStop(TimeStampedModel):
    """Individual stop on a bus route."""

    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name="stops")
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    pickup_time = models.TimeField()
    drop_time = models.TimeField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "bus_stops"
        ordering = ["order"]

    def __str__(self):
        return f"{self.route.code} - Stop {self.order}: {self.name}"


class StudentTransport(TimeStampedModel):
    """Student assignment to a bus route and stop."""

    BOARDING_TYPE_CHOICES = [
        ("pickup", "Pickup"),
        ("drop", "Drop"),
        ("both", "Both"),
    ]

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transport_assignments")
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name="student_assignments")
    stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name="student_assignments")
    boarding_type = models.CharField(max_length=10, choices=BOARDING_TYPE_CHOICES, default="both")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_transport"

    def __str__(self):
        return f"{self.student} - {self.route.code}"


class GPSTracking(TimeStampedModel):
    """GPS location data for vehicles."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="gps_records")
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    heading = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "gps_tracking"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.vehicle.vehicle_number} @ {self.timestamp}"
