from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, IsTeacher

from .models import EmergencyContact, Parent, Student, StudentDocument, StudentParent, StudentPromotion
from .serializers import (
    EmergencyContactSerializer,
    ParentSerializer,
    StudentDocumentSerializer,
    StudentListSerializer,
    StudentParentSerializer,
    StudentPromotionSerializer,
    StudentSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "current_class", "current_section", "status", "gender"]
    search_fields = ["student_id", "user__first_name", "user__last_name", "user__email"]
    ordering_fields = ["student_id", "user__first_name", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        return StudentSerializer

    def get_queryset(self):
        qs = Student.objects.select_related("user", "current_class", "current_section", "school")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(user=user)
        elif user.role == "parent":
            qs = qs.filter(parent_links__parent__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs


class ParentViewSet(viewsets.ModelViewSet):
    serializer_class = ParentSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]

    def get_queryset(self):
        qs = Parent.objects.select_related("user").prefetch_related("student_links__student__user")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class StudentParentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentParentSerializer
    permission_classes = [IsSchoolAdmin]

    def get_queryset(self):
        return StudentParent.objects.select_related("student__user", "parent__user")


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        qs = EmergencyContact.objects.select_related("student")
        student_id = self.request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class StudentDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentDocumentSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "document_type", "is_verified"]

    def get_queryset(self):
        qs = StudentDocument.objects.select_related("student", "verified_by")
        if self.request.user.role == "student":
            qs = qs.filter(student__user=self.request.user)
        return qs

    @action(detail=True, methods=["post"], permission_classes=[IsSchoolAdmin])
    def verify(self, request, pk=None):
        doc = self.get_object()
        doc.is_verified = True
        doc.verified_by = request.user
        doc.verified_at = timezone.now()
        doc.save(update_fields=["is_verified", "verified_by", "verified_at"])
        return Response({"detail": "Document verified."})


class StudentPromotionViewSet(viewsets.ModelViewSet):
    serializer_class = StudentPromotionSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["academic_year", "from_class", "to_class"]

    def get_queryset(self):
        return StudentPromotion.objects.select_related(
            "student__user", "from_class", "to_class", "academic_year"
        )

    def perform_create(self, serializer):
        promotion = serializer.save(promoted_by=self.request.user)
        # Update student's current class and section
        student = promotion.student
        student.current_class = promotion.to_class
        student.current_section = promotion.to_section
        student.status = "promoted"
        student.save(update_fields=["current_class", "current_section", "status"])
