from django.contrib import admin

from .models import AuditLog, DataExportLog, LoginAttempt


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "model_name", "object_repr", "ip_address", "timestamp")
    list_filter = ("action", "model_name")
    search_fields = ("object_repr", "model_name", "user__email")
    date_hierarchy = "timestamp"
    readonly_fields = ("user", "school", "action", "model_name", "object_id", "object_repr",
                       "changes", "ip_address", "user_agent", "timestamp")


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("email", "ip_address", "success", "failure_reason", "timestamp")
    list_filter = ("success",)
    search_fields = ("email", "ip_address")
    date_hierarchy = "timestamp"
    readonly_fields = ("email", "ip_address", "user_agent", "success", "failure_reason", "timestamp")


@admin.register(DataExportLog)
class DataExportLogAdmin(admin.ModelAdmin):
    list_display = ("user", "export_type", "model_name", "record_count", "file_format", "exported_at")
    list_filter = ("export_type", "file_format")
    search_fields = ("model_name", "user__email")
    date_hierarchy = "exported_at"
