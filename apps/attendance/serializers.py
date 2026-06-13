from rest_framework import serializers
from .models import AttendanceAlert, PeriodAttendance, StudentAttendance, TeacherAttendance


class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_id = serializers.CharField(source="student.student_id", read_only=True)

    class Meta:
        model = StudentAttendance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "marked_by")


class BulkAttendanceSerializer(serializers.Serializer):
    """For marking attendance for an entire class at once."""

    date = serializers.DateField()
    class_id = serializers.UUIDField()
    section_id = serializers.UUIDField(required=False)
    academic_year_id = serializers.UUIDField()
    records = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="List of {student_id, status, remarks}",
    )


class PeriodAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = PeriodAttendance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "marked_by")


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.user.full_name", read_only=True)

    class Meta:
        model = TeacherAttendance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AttendanceAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AttendanceAlert
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AttendanceReportSerializer(serializers.Serializer):
    """For attendance reports."""

    student_id = serializers.CharField()
    student_name = serializers.CharField()
    total_days = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    percentage = serializers.FloatField()
