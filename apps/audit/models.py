from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("export", "Export"),
        ("import", "Import"),
        ("view", "View"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    school = models.ForeignKey(
        "core.School", on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255)
    object_id = models.CharField(max_length=255, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} - {self.model_name} by {self.user}"


class LoginAttempt(TimeStampedModel):
    email = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "login_attempts"
        ordering = ["-timestamp"]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} - {self.email} at {self.timestamp}"


class DataExportLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="data_exports"
    )
    school = models.ForeignKey(
        "core.School", on_delete=models.SET_NULL, null=True, blank=True, related_name="data_exports"
    )
    export_type = models.CharField(max_length=100)
    model_name = models.CharField(max_length=255)
    record_count = models.PositiveIntegerField()
    file_format = models.CharField(max_length=20)
    file = models.FileField(upload_to="exports/", blank=True)
    exported_at = models.DateTimeField(auto_now_add=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "data_export_logs"

    def __str__(self):
        return f"{self.export_type} - {self.model_name} ({self.record_count} records)"
