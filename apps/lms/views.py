from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsTeacher

from .models import Assignment, AssignmentSubmission, Course, DiscussionForum, ForumPost, Lesson, LiveClass, Module
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    CourseListSerializer,
    CourseSerializer,
    DiscussionForumSerializer,
    ForumPostSerializer,
    LessonSerializer,
    LiveClassSerializer,
    ModuleSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacher]
    filterset_fields = ["school", "class_obj", "subject", "instructor", "is_published"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        qs = Course.objects.select_related("instructor", "subject", "class_obj").prefetch_related("modules__lessons")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        if self.request.user.role == "student":
            qs = qs.filter(is_published=True)
        return qs


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["course"]

    def get_queryset(self):
        return Module.objects.select_related("course").prefetch_related("lessons")


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["module", "content_type"]

    def get_queryset(self):
        return Lesson.objects.select_related("module__course")


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["class_obj", "subject", "teacher", "is_published", "assignment_type"]
    search_fields = ["title"]

    def get_queryset(self):
        qs = Assignment.objects.select_related("class_obj", "subject", "teacher")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(
                class_obj=user.student_profile.current_class,
                is_published=True,
            )
        elif user.role == "teacher":
            qs = qs.filter(teacher=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["assignment", "student", "status"]

    def get_queryset(self):
        qs = AssignmentSubmission.objects.select_related("student__user", "assignment", "graded_by")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "teacher":
            qs = qs.filter(assignment__teacher=user)
        return qs

    def perform_create(self, serializer):
        assignment = serializer.validated_data["assignment"]
        is_late = timezone.now() > assignment.due_date
        serializer.save(is_late=is_late, status="late" if is_late else "submitted")

    @action(detail=True, methods=["post"], permission_classes=[IsTeacher])
    def grade(self, request, pk=None):
        submission = self.get_object()
        marks = request.data.get("marks_obtained")
        feedback = request.data.get("feedback", "")
        if marks is None:
            return Response({"detail": "marks_obtained is required."}, status=400)
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.status = "graded"
        submission.save(update_fields=["marks_obtained", "feedback", "graded_by", "graded_at", "status"])
        return Response({"detail": "Submission graded."})


class LiveClassViewSet(viewsets.ModelViewSet):
    serializer_class = LiveClassSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["class_obj", "subject", "teacher", "platform"]
    ordering_fields = ["scheduled_at"]

    def get_queryset(self):
        return LiveClass.objects.select_related("class_obj", "subject", "teacher")


class DiscussionForumViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionForumSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "is_locked"]

    def get_queryset(self):
        return DiscussionForum.objects.select_related("course")


class ForumPostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["forum", "author", "is_pinned"]

    def get_queryset(self):
        return ForumPost.objects.select_related("author", "forum").prefetch_related("replies")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
