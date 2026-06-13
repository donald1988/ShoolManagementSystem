from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"widgets", views.DashboardWidgetViewSet, basename="dashboard-widget")
router.register(r"reports", views.ReportViewSet, basename="report")
router.register(r"executions", views.ReportExecutionViewSet, basename="report-execution")
router.register(r"predictions", views.AIPredictionViewSet, basename="ai-prediction")

urlpatterns = [
    path("", include(router.urls)),
]
