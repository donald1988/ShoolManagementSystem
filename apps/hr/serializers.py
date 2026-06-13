from rest_framework import serializers

from .models import (
    Employee,
    EmployeeContract,
    JobApplication,
    LeaveRequest,
    LeaveType,
    PerformanceReview,
    Recruitment,
)


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EmployeeContractSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.get_full_name", read_only=True)

    class Meta:
        model = EmployeeContract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "approved_by", "approved_at")


class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    reviewer_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)

    class Meta:
        model = PerformanceReview
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RecruitmentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    posted_by_name = serializers.CharField(source="posted_by.get_full_name", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Recruitment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_application_count(self, obj):
        return obj.applications.count()


class JobApplicationSerializer(serializers.ModelSerializer):
    recruitment_position = serializers.CharField(source="recruitment.position", read_only=True)

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
