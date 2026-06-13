from rest_framework import serializers

from .models import Asset, AssetCategory, AssetMaintenance, AssetTransfer


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)

    class Meta:
        model = Asset
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_code = serializers.CharField(source="asset.asset_code", read_only=True)

    class Meta:
        model = AssetMaintenance
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AssetTransferSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    asset_code = serializers.CharField(source="asset.asset_code", read_only=True)
    from_user_name = serializers.CharField(source="from_user.full_name", read_only=True, default=None)
    to_user_name = serializers.CharField(source="to_user.full_name", read_only=True, default=None)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = AssetTransfer
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
