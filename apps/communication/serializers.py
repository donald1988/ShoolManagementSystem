from rest_framework import serializers

from .models import Announcement, EmergencyAlert, Message, Notification, NotificationTemplate


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.get_full_name", read_only=True)

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "is_read", "read_at")


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    target_class_name = serializers.CharField(source="target_class.name", read_only=True)

    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EmergencyAlertSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source="sent_by.get_full_name", read_only=True)

    class Meta:
        model = EmergencyAlert
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
