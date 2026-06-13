from collections import defaultdict

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, IsTeacher

from .models import Period, Room, TimetableChange, TimetableEntry
from .serializers import (
    PeriodSerializer,
    RoomSerializer,
    TimetableChangeSerializer,
    TimetableEntrySerializer,
)


class PeriodViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_break"]

    def get_queryset(self):
        qs = Period.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "room_type", "is_available"]
    search_fields = ["name", "code", "building"]

    def get_queryset(self):
        qs = Room.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class TimetableEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["class_obj", "section", "teacher", "day_of_week", "academic_year", "is_active"]
    search_fields = ["subject__name", "teacher__first_name", "teacher__last_name"]

    def get_queryset(self):
        qs = TimetableEntry.objects.select_related(
            "class_obj", "section", "subject", "teacher", "room", "period", "academic_year"
        )
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=False, methods=["get"], url_path="by-class")
    def by_class(self, request):
        """Return timetable grouped by day for a given class."""
        class_id = request.query_params.get("class_id")
        section_id = request.query_params.get("section_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not class_id:
            return Response({"error": "class_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        entries = self.get_queryset().filter(class_obj_id=class_id, is_active=True)
        if section_id:
            entries = entries.filter(section_id=section_id)
        if academic_year_id:
            entries = entries.filter(academic_year_id=academic_year_id)

        grouped = defaultdict(list)
        for entry in entries.order_by("period__order"):
            grouped[entry.day_of_week].append(TimetableEntrySerializer(entry).data)

        return Response(grouped)

    @action(detail=False, methods=["get"], url_path="by-teacher")
    def by_teacher(self, request):
        """Return timetable for a given teacher."""
        teacher_id = request.query_params.get("teacher_id")
        academic_year_id = request.query_params.get("academic_year_id")

        if not teacher_id:
            return Response({"error": "teacher_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        entries = self.get_queryset().filter(teacher_id=teacher_id, is_active=True)
        if academic_year_id:
            entries = entries.filter(academic_year_id=academic_year_id)

        grouped = defaultdict(list)
        for entry in entries.order_by("period__order"):
            grouped[entry.day_of_week].append(TimetableEntrySerializer(entry).data)

        return Response(grouped)


class TimetableChangeViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableChangeSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["original_entry", "date"]

    def get_queryset(self):
        return TimetableChange.objects.select_related(
            "original_entry", "substitute_teacher", "substitute_subject", "substitute_room", "changed_by"
        )
