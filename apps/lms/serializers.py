from rest_framework import serializers
from .models import Assignment, AssignmentSubmission, Course, DiscussionForum, ForumPost, Lesson, LiveClass, Module


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "title", "description", "instructor_name", "thumbnail", "is_published", "module_count")

    def get_module_count(self, obj):
        return obj.modules.count()


class AssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)

    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "graded_by", "graded_at")


class LiveClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = LiveClass
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_replies(self, obj):
        if obj.replies.exists():
            return ForumPostSerializer(obj.replies.all()[:10], many=True).data
        return []


class DiscussionForumSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionForum
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_post_count(self, obj):
        return obj.posts.count()
