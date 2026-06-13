from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"categories", views.AssetCategoryViewSet, basename="asset-category")
router.register(r"assets", views.AssetViewSet, basename="asset")
router.register(r"maintenance", views.AssetMaintenanceViewSet, basename="asset-maintenance")
router.register(r"transfers", views.AssetTransferViewSet, basename="asset-transfer")

urlpatterns = [
    path("", include(router.urls)),
]
