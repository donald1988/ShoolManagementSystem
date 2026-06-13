from django.contrib import admin

from .models import Announcement, EmergencyAlert, Message, Notification, NotificationTemplate


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "subject", "is_read", "created_at")
    list_filter = ("is_read", "school")
    search_fields = ("subject", "body", "sender__first_name", "recipient__first_name")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "author", "target_audience", "is_pinned", "publish_date", "is_active")
    list_filter = ("school", "target_audience", "is_pinned", "is_active")
    search_fields = ("title", "content")


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "notification_type", "event_trigger")
    list_filter = ("school", "notification_type")
    search_fields = ("name", "subject")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "message")


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "severity", "sent_by", "is_active", "created_at")
    list_filter = ("school", "severity", "is_active")
    search_fields = ("title", "message")
