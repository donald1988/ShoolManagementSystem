from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Course(TimeStampedModel):
    """LMS course container."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="courses")
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="instructed_courses"
    )
    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "lms_courses"

    def __str__(self):
        return self.title


class Module(TimeStampedModel):
    """Module within a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "lms_modules"
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(TimeStampedModel):
    """Individual lesson/content within a module."""

    CONTENT_TYPES = [
        ("text", "Text"),
        ("video", "Video"),
        ("pdf", "PDF"),
        ("link", "External Link"),
        ("quiz", "Quiz"),
        ("live_class", "Live Class"),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default="text")
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    file = models.FileField(upload_to="courses/lessons/", blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "lms_lessons"
        ordering = ["order"]

    def __str__(self):
        return self.title


class Assignment(TimeStampedModel):
    """Assignments for students."""

    ASSIGNMENT_TYPES = [
        ("homework", "Homework"),
        ("project", "Project"),
        ("essay", "Essay"),
        ("lab_report", "Lab Report"),
        ("presentation", "Presentation"),
        ("other", "Other"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments", null=True, blank=True)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="assignments")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_assignments")
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default="homework")
    due_date = models.DateTimeField()
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    file = models.FileField(upload_to="assignments/", blank=True)
    is_published = models.BooleanField(default=False)
    allow_late_submission = models.BooleanField(default=False)
    late_penalty_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta(TimeStampedModel.Meta):
        db_table = "assignments"

    def __str__(self):
        return self.title


class AssignmentSubmission(TimeStampedModel):
    """Student assignment submissions."""

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("late", "Late"),
        ("graded", "Graded"),
        ("returned", "Returned"),
        ("resubmitted", "Resubmitted"),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to="submissions/")
    text_response = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="submitted")
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="graded_submissions"
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "assignment_submissions"
        unique_together = [("assignment", "student")]

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"


class LiveClass(TimeStampedModel):
    """Scheduled live classes / video conferences."""

    PLATFORM_CHOICES = [
        ("zoom", "Zoom"),
        ("teams", "Microsoft Teams"),
        ("meet", "Google Meet"),
        ("custom", "Custom"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_classes", null=True, blank=True)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="live_classes")
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="live_classes")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default="zoom")
    meeting_url = models.URLField()
    meeting_id = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=50, blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    recording_url = models.URLField(blank=True)
    is_recurring = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "live_classes"
        verbose_name_plural = "Live Classes"

    def __str__(self):
        return f"{self.title} ({self.scheduled_at})"


class DiscussionForum(TimeStampedModel):
    """Discussion forum for a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="forums")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "discussion_forums"

    def __str__(self):
        return self.title


class ForumPost(TimeStampedModel):
    """Individual posts in a discussion forum."""

    forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_posts")
    parent_post = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "forum_posts"

    def __str__(self):
        return f"Post by {self.author.full_name} in {self.forum.title}"
