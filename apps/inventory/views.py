from rest_framework import viewsets

from apps.core.permissions import IsSchoolAdmin

from .models import Asset, AssetCategory, AssetMaintenance, AssetTransfer
from .serializers import (
    AssetCategorySerializer,
    AssetMaintenanceSerializer,
    AssetSerializer,
    AssetTransferSerializer,
)


class AssetCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AssetCategorySerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school"]
    search_fields = ["name"]

    def get_queryset(self):
        qs = AssetCategory.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "category", "condition", "status", "assigned_to"]
    search_fields = ["name", "asset_code", "serial_number"]

    def get_queryset(self):
        qs = Asset.objects.select_related("category", "assigned_to")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = AssetMaintenanceSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["asset", "maintenance_type", "status"]

    def get_queryset(self):
        return AssetMaintenance.objects.select_related("asset")


class AssetTransferViewSet(viewsets.ModelViewSet):
    serializer_class = AssetTransferSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["asset", "from_user", "to_user"]

    def get_queryset(self):
        return AssetTransfer.objects.select_related("asset", "from_user", "to_user", "approved_by")
