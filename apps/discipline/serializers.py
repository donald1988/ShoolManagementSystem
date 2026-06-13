from rest_framework import serializers

from .models import BehaviorCategory, BehaviorPoints, Detention, DisciplineIncident, Suspension


class BehaviorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DisciplineIncidentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = DisciplineIncident
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "reported_by", "resolved_by", "resolved_at")


class DetentionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = Detention
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SuspensionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True)

    class Meta:
        model = Suspension
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BehaviorPointsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = BehaviorPoints
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
