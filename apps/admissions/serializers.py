from rest_framework import serializers
from .models import AdmissionApplication, AdmissionDocument, AdmissionPeriod, SeatAllocation


class AdmissionPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionPeriod
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AdmissionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    documents = AdmissionDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "application_number", "reviewed_by", "student")


class AdmissionApplicationListSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="applying_for_class.name", read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = (
            "id", "application_number", "first_name", "last_name",
            "email", "class_name", "status", "merit_score", "created_at",
        )


class SeatAllocationSerializer(serializers.ModelSerializer):
    available_seats = serializers.ReadOnlyField()
    class_name = serializers.CharField(source="class_obj.name", read_only=True)

    class Meta:
        model = SeatAllocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
