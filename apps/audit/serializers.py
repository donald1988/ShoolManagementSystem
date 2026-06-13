from rest_framework import serializers

from .models import AuditLog, DataExportLog, LoginAttempt


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "timestamp")


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "timestamp")


class DataExportLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = DataExportLog
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "exported_at")
