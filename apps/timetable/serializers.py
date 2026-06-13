from rest_framework import serializers

from .models import Period, Room, TimetableChange, TimetableEntry


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TimetableEntrySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True, default=None)
    room_name = serializers.CharField(source="room.name", read_only=True, default=None)
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        model = TimetableEntry
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TimetableChangeSerializer(serializers.ModelSerializer):
    original_entry_display = serializers.StringRelatedField(source="original_entry", read_only=True)
    substitute_teacher_name = serializers.CharField(
        source="substitute_teacher.full_name", read_only=True, default=None
    )
    substitute_subject_name = serializers.CharField(
        source="substitute_subject.name", read_only=True, default=None
    )
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = TimetableChange
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
