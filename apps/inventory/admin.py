from django.contrib import admin

from .models import Asset, AssetCategory, AssetMaintenance, AssetTransfer


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "school")
    list_filter = ("school",)
    search_fields = ("name",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("asset_code", "name", "category", "condition", "status", "location", "assigned_to")
    list_filter = ("school", "category", "condition", "status")
    search_fields = ("name", "asset_code", "serial_number")


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = ("asset", "maintenance_type", "scheduled_date", "completed_date", "cost", "status")
    list_filter = ("maintenance_type", "status")
    search_fields = ("asset__asset_code", "asset__name")


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ("asset", "from_location", "to_location", "transfer_date", "approved_by")
    list_filter = ("transfer_date",)
    search_fields = ("asset__asset_code", "asset__name")
