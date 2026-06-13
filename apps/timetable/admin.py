from django.contrib import admin

from .models import Period, Room, TimetableChange, TimetableEntry


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "start_time", "end_time", "order", "is_break")
    list_filter = ("school", "is_break")
    ordering = ("school", "order")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "building", "floor", "room_type", "capacity", "is_available")
    list_filter = ("school", "room_type", "is_available")
    search_fields = ("name", "code", "building")


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "section", "subject", "teacher", "period", "day_of_week", "is_active")
    list_filter = ("day_of_week", "academic_year", "class_obj", "is_active")
    search_fields = ("subject__name", "teacher__first_name", "teacher__last_name")


@admin.register(TimetableChange)
class TimetableChangeAdmin(admin.ModelAdmin):
    list_display = ("original_entry", "date", "substitute_teacher", "changed_by")
    list_filter = ("date",)
    search_fields = ("reason",)
