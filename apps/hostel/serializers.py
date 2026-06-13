from rest_framework import serializers

from .models import Bed, Building, Floor, HostelAllocation, Room


class BuildingSerializer(serializers.ModelSerializer):
    warden_name = serializers.CharField(source="warden.full_name", read_only=True, default=None)

    class Meta:
        model = Building
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FloorSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Floor
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RoomSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source="floor.name", read_only=True)
    building_name = serializers.CharField(source="floor.building.name", read_only=True)

    class Meta:
        model = Room
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BedSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)

    class Meta:
        model = Bed
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class HostelAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    allocated_by_name = serializers.CharField(source="allocated_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelAllocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
