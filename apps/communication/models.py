from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Message(TimeStampedModel):
    """Direct message between users."""

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    parent_message = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )
    is_archived_sender = models.BooleanField(default=False)
    is_archived_recipient = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "communication_messages"

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.subject}"


class Announcement(TimeStampedModel):
    """School-wide or targeted announcements."""

    TARGET_AUDIENCE_CHOICES = [
        ("all", "All"),
        ("students", "Students"),
        ("teachers", "Teachers"),
        ("parents", "Parents"),
        ("staff", "Staff"),
    ]

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="announcements"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcements"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE_CHOICES, default="all")
    target_class = models.ForeignKey(
        "academics.Class",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
    )
    is_pinned = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "communication_announcements"

    def __str__(self):
        return self.title


class NotificationTemplate(TimeStampedModel):
    """Templates for various notification types."""

    NOTIFICATION_TYPES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push Notification"),
        ("in_app", "In-App"),
    ]

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="notification_templates"
    )
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    body_template = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    event_trigger = models.CharField(max_length=100, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "communication_notification_templates"
        unique_together = [("school", "name")]

    def __str__(self):
        return f"{self.name} ({self.notification_type})"


class Notification(TimeStampedModel):
    """User notification."""

    NOTIFICATION_TYPES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push Notification"),
        ("in_app", "In-App"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default="in_app")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.URLField(blank=True)
    data = models.JSONField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "communication_notifications"

    def __str__(self):
        return f"{self.recipient}: {self.title}"


class EmergencyAlert(TimeStampedModel):
    """Emergency alerts for the school."""

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="emergency_alerts"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="info")
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_alerts"
    )
    is_active = models.BooleanField(default=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "communication_emergency_alerts"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
