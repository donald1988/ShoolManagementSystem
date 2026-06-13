from rest_framework import serializers

from .models import HealthIncident, HealthVisit, MedicalRecord, Vaccination


class MedicalRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class VaccinationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = Vaccination
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class HealthVisitSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    attended_by_name = serializers.CharField(source="attended_by.full_name", read_only=True)

    class Meta:
        model = HealthVisit
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class HealthIncidentSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)

    class Meta:
        model = HealthIncident
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
