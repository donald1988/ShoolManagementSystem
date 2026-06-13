from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"salary-structures", views.SalaryStructureViewSet, basename="salary-structure")
router.register(r"employee-salaries", views.EmployeeSalaryViewSet, basename="employee-salary")
router.register(r"payslips", views.PayslipViewSet, basename="payslip")
router.register(r"payroll-runs", views.PayrollRunViewSet, basename="payroll-run")

urlpatterns = [
    path("", include(router.urls)),
]
