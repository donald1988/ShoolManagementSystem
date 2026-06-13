from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"categories", views.BehaviorCategoryViewSet, basename="behavior-category")
router.register(r"incidents", views.DisciplineIncidentViewSet, basename="discipline-incident")
router.register(r"detentions", views.DetentionViewSet, basename="detention")
router.register(r"suspensions", views.SuspensionViewSet, basename="suspension")
router.register(r"points", views.BehaviorPointsViewSet, basename="behavior-points")

urlpatterns = [
    path("", include(router.urls)),
]
