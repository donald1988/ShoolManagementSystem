from django.contrib import admin

from .models import AcademicYear, Campus, School, SystemConfiguration, Term


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "country", "is_active", "subscription_plan")
    list_filter = ("is_active", "subscription_plan", "country")
    search_fields = ("name", "code", "email")


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "code", "city", "is_active", "is_main")
    list_filter = ("is_active", "is_main", "school")
    search_fields = ("name", "code")


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "school")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "term_type", "start_date", "end_date", "is_current")
    list_filter = ("term_type", "is_current")


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ("key", "school", "value")
    search_fields = ("key",)
    list_filter = ("school",)
