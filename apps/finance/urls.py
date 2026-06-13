from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"fee-categories", views.FeeCategoryViewSet, basename="fee-category")
router.register(r"fee-structures", views.FeeStructureViewSet, basename="fee-structure")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"scholarships", views.ScholarshipViewSet, basename="scholarship")
router.register(r"student-scholarships", views.StudentScholarshipViewSet, basename="student-scholarship")
router.register(r"fee-waivers", views.FeeWaiverViewSet, basename="fee-waiver")

urlpatterns = [
    path("", include(router.urls)),
]
