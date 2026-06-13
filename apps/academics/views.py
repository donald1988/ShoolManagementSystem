from rest_framework import viewsets

from apps.core.permissions import IsSchoolAdmin, IsTeacher

from .models import Class, ClassSubject, Department, Enrollment, Section, Subject, Teacher
from .serializers import (
    ClassSerializer,
    ClassSubjectSerializer,
    DepartmentSerializer,
    EnrollmentSerializer,
    SectionSerializer,
    SubjectSerializer,
    TeacherSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_active"]
    search_fields = ["name", "code"]

    def get_queryset(self):
        qs = Department.objects.select_related("head")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class ClassViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["numeric_level"]

    def get_queryset(self):
        qs = Class.objects.prefetch_related("sections", "students")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["class_obj", "is_active"]

    def get_queryset(self):
        return Section.objects.select_related("class_obj", "class_teacher")


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "department", "subject_type", "is_active", "is_mandatory"]
    search_fields = ["name", "code"]

    def get_queryset(self):
        qs = Subject.objects.select_related("department")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class ClassSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["class_obj", "subject", "academic_year", "teacher"]

    def get_queryset(self):
        return ClassSubject.objects.select_related("class_obj", "subject", "teacher", "academic_year")


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "department", "is_active"]
    search_fields = ["employee_id", "user__first_name", "user__last_name"]

    def get_queryset(self):
        qs = Teacher.objects.select_related("user", "department")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["class_obj", "section", "academic_year", "is_active"]
    search_fields = ["student__student_id", "student__user__first_name"]

    def get_queryset(self):
        return Enrollment.objects.select_related("student__user", "class_obj", "section", "academic_year")
