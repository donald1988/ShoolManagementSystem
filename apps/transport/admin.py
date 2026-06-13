from django.contrib import admin

from .models import BusRoute, BusStop, Driver, GPSTracking, StudentTransport, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_number", "vehicle_type", "make", "model", "capacity", "is_active")
    list_filter = ("school", "vehicle_type", "fuel_type", "is_active")
    search_fields = ("vehicle_number", "make", "model")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "license_number", "license_expiry", "is_active")
    list_filter = ("school", "is_active")
    search_fields = ("name", "phone", "license_number")


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "start_location", "end_location", "monthly_fee", "is_active")
    list_filter = ("school", "is_active")
    search_fields = ("name", "code")


@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ("name", "route", "order", "pickup_time", "drop_time")
    list_filter = ("route",)
    search_fields = ("name",)


@admin.register(StudentTransport)
class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ("student", "route", "stop", "boarding_type", "start_date", "is_active")
    list_filter = ("boarding_type", "is_active")
    search_fields = ("student__user__first_name", "student__user__last_name")


@admin.register(GPSTracking)
class GPSTrackingAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "latitude", "longitude", "speed", "timestamp")
    list_filter = ("vehicle",)
