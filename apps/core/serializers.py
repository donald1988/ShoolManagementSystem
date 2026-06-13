from rest_framework import serializers

from .models import AcademicYear, Campus, School, SystemConfiguration, Term


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampusSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Campus
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AcademicYearSerializer(serializers.ModelSerializer):
    terms = serializers.SerializerMethodField()

    class Meta:
        model = AcademicYear
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_terms(self, obj):
        return TermSerializer(obj.terms.all(), many=True).data


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SystemConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfiguration
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
