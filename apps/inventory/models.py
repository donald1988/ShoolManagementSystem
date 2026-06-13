from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AssetCategory(TimeStampedModel):
    """Category for grouping assets."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="asset_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "asset_categories"
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name


class Asset(TimeStampedModel):
    """School asset/inventory item."""

    CONDITION_CHOICES = [
        ("new", "New"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
        ("damaged", "Damaged"),
        ("disposed", "Disposed"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("in_use", "In Use"),
        ("maintenance", "Maintenance"),
        ("disposed", "Disposed"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="assets")
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets")
    name = models.CharField(max_length=255)
    asset_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_assets"
    )
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    warranty_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "assets"

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class AssetMaintenance(TimeStampedModel):
    """Maintenance record for an asset."""

    MAINTENANCE_TYPE_CHOICES = [
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("emergency", "Emergency"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="maintenance_records")
    maintenance_type = models.CharField(max_length=15, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "asset_maintenance"

    def __str__(self):
        return f"{self.asset.asset_code} - {self.maintenance_type} ({self.scheduled_date})"


class AssetTransfer(TimeStampedModel):
    """Record of asset transfers between locations or users."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transfers")
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_transfers_from"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_transfers_to"
    )
    transfer_date = models.DateField()
    reason = models.TextField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_transfers"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "asset_transfers"

    def __str__(self):
        return f"{self.asset.asset_code}: {self.from_location} -> {self.to_location}"
