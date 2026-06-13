from django.contrib import admin

from .models import Bed, Building, Floor, HostelAllocation, Room


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "warden", "total_rooms", "is_active")
    list_filter = ("school", "is_active")
    search_fields = ("name", "code")


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "floor_number", "total_rooms")
    list_filter = ("building",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "floor", "room_type", "capacity", "occupied", "monthly_fee", "is_available")
    list_filter = ("room_type", "is_available", "has_ac")
    search_fields = ("room_number",)


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "room", "is_occupied", "student")
    list_filter = ("is_occupied",)


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ("student", "room", "bed", "academic_year", "check_in_date", "check_out_date", "is_active")
    list_filter = ("academic_year", "is_active")
    search_fields = ("student__user__first_name", "student__user__last_name")
