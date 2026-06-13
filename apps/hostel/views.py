from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin

from .models import Bed, Building, Floor, HostelAllocation, Room
from .serializers import (
    BedSerializer,
    BuildingSerializer,
    FloorSerializer,
    HostelAllocationSerializer,
    RoomSerializer,
)


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_active"]
    search_fields = ["name", "code"]

    def get_queryset(self):
        qs = Building.objects.select_related("warden")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class FloorViewSet(viewsets.ModelViewSet):
    serializer_class = FloorSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["building"]

    def get_queryset(self):
        return Floor.objects.select_related("building")


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["floor", "room_type", "is_available"]
    search_fields = ["room_number"]

    def get_queryset(self):
        return Room.objects.select_related("floor__building")


class BedViewSet(viewsets.ModelViewSet):
    serializer_class = BedSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["room", "is_occupied"]

    def get_queryset(self):
        return Bed.objects.select_related("room", "student")


class HostelAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["student", "room", "academic_year", "is_active"]

    def get_queryset(self):
        return HostelAllocation.objects.select_related("student", "room", "bed", "academic_year", "allocated_by")

    @action(detail=True, methods=["post"])
    def check_in(self, request, pk=None):
        """Mark a student as checked in."""
        allocation = self.get_object()
        if allocation.check_in_date and allocation.is_active:
            return Response({"detail": "Student is already checked in."}, status=status.HTTP_400_BAD_REQUEST)
        allocation.check_in_date = date.today()
        allocation.is_active = True
        allocation.save(update_fields=["check_in_date", "is_active", "updated_at"])

        # Update room occupancy
        allocation.room.occupied = min(allocation.room.occupied + 1, allocation.room.capacity)
        allocation.room.save(update_fields=["occupied"])

        # Update bed status if assigned
        if allocation.bed:
            allocation.bed.is_occupied = True
            allocation.bed.student = allocation.student
            allocation.bed.save(update_fields=["is_occupied", "student"])

        return Response(HostelAllocationSerializer(allocation).data)

    @action(detail=True, methods=["post"])
    def check_out(self, request, pk=None):
        """Mark a student as checked out."""
        allocation = self.get_object()
        if not allocation.is_active:
            return Response({"detail": "Allocation is not active."}, status=status.HTTP_400_BAD_REQUEST)
        allocation.check_out_date = date.today()
        allocation.is_active = False
        allocation.save(update_fields=["check_out_date", "is_active", "updated_at"])

        # Update room occupancy
        allocation.room.occupied = max(0, allocation.room.occupied - 1)
        allocation.room.save(update_fields=["occupied"])

        # Free the bed if assigned
        if allocation.bed:
            allocation.bed.is_occupied = False
            allocation.bed.student = None
            allocation.bed.save(update_fields=["is_occupied", "student"])

        return Response(HostelAllocationSerializer(allocation).data)
