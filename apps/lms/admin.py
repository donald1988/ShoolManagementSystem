from django.contrib import admin
from .models import Assignment, AssignmentSubmission, Course, DiscussionForum, ForumPost, Lesson, LiveClass, Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "class_obj", "subject", "is_published")
    list_filter = ("is_published", "school")
    search_fields = ("title",)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "content_type", "duration_minutes", "order")
    list_filter = ("content_type",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "class_obj", "subject", "teacher", "due_date", "is_published")
    list_filter = ("assignment_type", "is_published", "class_obj")
    search_fields = ("title",)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "status", "marks_obtained", "is_late")
    list_filter = ("status", "is_late")


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "class_obj", "platform", "scheduled_at")
    list_filter = ("platform",)


@admin.register(DiscussionForum)
class DiscussionForumAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_locked")


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ("forum", "author", "is_pinned", "created_at")
    list_filter = ("is_pinned",)
