from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, IsTeacher

from .models import Exam, ExamSchedule, ExamSeatingPlan, ExamType, Grade, GradeRange, GradingScale, ReportCard
from .serializers import (
    ExamScheduleSerializer,
    ExamSeatingPlanSerializer,
    ExamSerializer,
    ExamTypeSerializer,
    GradeRangeSerializer,
    GradeSerializer,
    GradingScaleSerializer,
    ReportCardSerializer,
)


class ExamTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ExamTypeSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_active"]

    def get_queryset(self):
        qs = ExamType.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "academic_year", "term", "exam_type", "is_published"]
    search_fields = ["name"]

    def get_queryset(self):
        qs = Exam.objects.select_related("exam_type", "academic_year", "term").prefetch_related("schedules")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=True, methods=["post"], permission_classes=[IsSchoolAdmin])
    def publish(self, request, pk=None):
        exam = self.get_object()
        exam.is_published = True
        exam.save(update_fields=["is_published"])
        return Response({"detail": "Exam published."})


class ExamScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["exam", "class_obj", "subject", "date"]

    def get_queryset(self):
        return ExamSchedule.objects.select_related("exam", "class_obj", "subject", "invigilator")


class ExamSeatingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSeatingPlanSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["exam_schedule"]

    def get_queryset(self):
        return ExamSeatingPlan.objects.select_related("student__user", "exam_schedule")


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "exam_schedule", "exam_schedule__exam"]
    search_fields = ["student__student_id", "student__user__first_name"]

    def get_queryset(self):
        qs = Grade.objects.select_related("student__user", "exam_schedule__subject", "graded_by")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)


class GradingScaleViewSet(viewsets.ModelViewSet):
    serializer_class = GradingScaleSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school"]

    def get_queryset(self):
        qs = GradingScale.objects.prefetch_related("ranges")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class GradeRangeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeRangeSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["grading_scale"]

    def get_queryset(self):
        return GradeRange.objects.select_related("grading_scale")


class ReportCardViewSet(viewsets.ModelViewSet):
    serializer_class = ReportCardSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "academic_year", "term", "is_published"]

    def get_queryset(self):
        qs = ReportCard.objects.select_related("student__user", "academic_year", "term")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user, is_published=True)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user, is_published=True)
        return qs
