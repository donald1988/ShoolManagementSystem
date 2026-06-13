from rest_framework import serializers

from .models import EmergencyContact, Parent, Student, StudentDocument, StudentParent, StudentPromotion


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    class_name = serializers.CharField(source="current_class.name", read_only=True)
    section_name = serializers.CharField(source="current_section.name", read_only=True)

    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""

    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    class_name = serializers.CharField(source="current_class.name", read_only=True)
    section_name = serializers.CharField(source="current_section.name", read_only=True)

    class Meta:
        model = Student
        fields = (
            "id", "student_id", "full_name", "email", "class_name",
            "section_name", "roll_number", "status", "photo",
        )


class ParentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Parent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_children(self, obj):
        links = obj.student_links.select_related("student__user")
        return [
            {
                "student_id": link.student.student_id,
                "name": link.student.user.full_name,
                "relationship": link.relationship,
            }
            for link in links
        ]


class StudentParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentParent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "verified_by", "verified_at")


class StudentPromotionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = StudentPromotion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
