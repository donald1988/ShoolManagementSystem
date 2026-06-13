from rest_framework import serializers
from .models import Class, ClassSubject, Department, Enrollment, Section, Subject, SubjectPrerequisite, Teacher


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source="head.full_name", read_only=True)

    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_sections(self, obj):
        return SectionSerializer(obj.sections.filter(is_active=True), many=True).data

    def get_student_count(self, obj):
        return obj.students.count()


class SectionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_obj.name", read_only=True)
    teacher_name = serializers.CharField(source="class_teacher.full_name", read_only=True)

    class Meta:
        model = Section
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubjectPrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPrerequisite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ClassSubjectSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_obj.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = ClassSubject
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
