from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"modules", views.ModuleViewSet, basename="module")
router.register(r"lessons", views.LessonViewSet, basename="lesson")
router.register(r"assignments", views.AssignmentViewSet, basename="assignment")
router.register(r"submissions", views.AssignmentSubmissionViewSet, basename="submission")
router.register(r"live-classes", views.LiveClassViewSet, basename="live-class")
router.register(r"forums", views.DiscussionForumViewSet, basename="forum")
router.register(r"forum-posts", views.ForumPostViewSet, basename="forum-post")

urlpatterns = [
    path("", include(router.urls)),
]
