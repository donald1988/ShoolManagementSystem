from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, ReadOnly

from .models import Announcement, EmergencyAlert, Message, Notification, NotificationTemplate
from .serializers import (
    AnnouncementSerializer,
    EmergencyAlertSerializer,
    MessageSerializer,
    NotificationSerializer,
    NotificationTemplateSerializer,
)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_read"]
    search_fields = ["subject", "body"]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related("sender", "recipient", "parent_message")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user, school=self.request.user.school)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient == request.user:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        return Response(MessageSerializer(message).data)

    @action(detail=False, methods=["get"])
    def inbox(self, request):
        qs = self.get_queryset().filter(recipient=request.user, is_archived_recipient=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        qs = self.get_queryset().filter(sender=request.user, is_archived_sender=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsSchoolAdmin | ReadOnly]
    filterset_fields = ["school", "target_audience", "is_pinned", "is_active"]
    search_fields = ["title", "content"]

    def get_queryset(self):
        qs = Announcement.objects.select_related("author", "school", "target_class")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsSchoolAdmin])
    def publish(self, request, pk=None):
        announcement = self.get_object()
        announcement.is_active = True
        announcement.publish_date = timezone.now()
        announcement.save()
        return Response(AnnouncementSerializer(announcement).data)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "notification_type"]
    search_fields = ["name", "subject"]

    def get_queryset(self):
        qs = NotificationTemplate.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["notification_type", "is_read"]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({"status": "all notifications marked as read"})


class EmergencyAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyAlertSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "severity", "is_active"]

    def get_queryset(self):
        qs = EmergencyAlert.objects.select_related("school", "sent_by")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_active = False
        alert.resolved_at = timezone.now()
        alert.save()
        return Response(EmergencyAlertSerializer(alert).data)
