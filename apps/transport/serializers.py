from rest_framework import serializers

from .models import BusRoute, BusStop, Driver, GPSTracking, StudentTransport, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DriverSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True, default=None)

    class Meta:
        model = Driver
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStop
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BusRouteSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True, default=None)
    driver_name = serializers.CharField(source="driver.name", read_only=True, default=None)
    stops = BusStopSerializer(many=True, read_only=True)

    class Meta:
        model = BusRoute
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentTransportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, default=None)
    route_name = serializers.CharField(source="route.name", read_only=True, default=None)
    stop_name = serializers.CharField(source="stop.name", read_only=True, default=None)

    class Meta:
        model = StudentTransport
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class GPSTrackingSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)

    class Meta:
        model = GPSTracking
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "recorded_at")
