from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsTransportManager

from .models import BusRoute, BusStop, Driver, GPSTracking, StudentTransport, Vehicle
from .serializers import (
    BusRouteSerializer,
    BusStopSerializer,
    DriverSerializer,
    GPSTrackingSerializer,
    StudentTransportSerializer,
    VehicleSerializer,
)


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["school", "vehicle_type", "fuel_type", "is_active"]
    search_fields = ["vehicle_number", "make", "model"]

    def get_queryset(self):
        qs = Vehicle.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=True, methods=["get"])
    def track(self, request, pk=None):
        """Get the latest GPS position for a vehicle."""
        vehicle = self.get_object()
        latest = GPSTracking.objects.filter(vehicle=vehicle).order_by("-timestamp").first()
        if not latest:
            return Response({"detail": "No GPS data available."}, status=status.HTTP_404_NOT_FOUND)
        return Response(GPSTrackingSerializer(latest).data)


class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["school", "is_active"]
    search_fields = ["name", "phone", "license_number"]

    def get_queryset(self):
        qs = Driver.objects.select_related("user")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class BusRouteViewSet(viewsets.ModelViewSet):
    serializer_class = BusRouteSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["school", "vehicle", "driver", "is_active"]
    search_fields = ["name", "code"]

    def get_queryset(self):
        qs = BusRoute.objects.select_related("vehicle", "driver").prefetch_related("stops")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class BusStopViewSet(viewsets.ModelViewSet):
    serializer_class = BusStopSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["route"]

    def get_queryset(self):
        return BusStop.objects.select_related("route")


class StudentTransportViewSet(viewsets.ModelViewSet):
    serializer_class = StudentTransportSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["student", "route", "stop", "boarding_type", "is_active"]

    def get_queryset(self):
        return StudentTransport.objects.select_related("student", "route", "stop")


class GPSTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = GPSTrackingSerializer
    permission_classes = [IsTransportManager]
    filterset_fields = ["vehicle"]

    def get_queryset(self):
        return GPSTracking.objects.select_related("vehicle")
