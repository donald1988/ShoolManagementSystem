from rest_framework import serializers
from .models import Exam, ExamSchedule, ExamSeatingPlan, ExamType, Grade, GradeRange, GradingScale, ReportCard


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)

    class Meta:
        model = ExamSchedule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ExamSerializer(serializers.ModelSerializer):
    schedules = ExamScheduleSerializer(many=True, read_only=True)
    exam_type_name = serializers.CharField(source="exam_type.name", read_only=True)

    class Meta:
        model = Exam
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ExamSeatingPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ExamSeatingPlan
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="exam_schedule.subject.name", read_only=True)
    percentage = serializers.ReadOnlyField()
    is_passed = serializers.ReadOnlyField()

    class Meta:
        model = Grade
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "graded_by")


class GradeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeRange
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class GradingScaleSerializer(serializers.ModelSerializer):
    ranges = GradeRangeSerializer(many=True, read_only=True)

    class Meta:
        model = GradingScale
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ReportCard
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
