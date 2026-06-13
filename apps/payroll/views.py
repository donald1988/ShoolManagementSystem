from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAccountant, IsHR

from .models import EmployeeSalary, PayrollRun, Payslip, SalaryStructure
from .serializers import EmployeeSalarySerializer, PayrollRunSerializer, PayslipSerializer, SalaryStructureSerializer


class SalaryStructureViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsHR]
    filterset_fields = ["school", "is_active"]

    def get_queryset(self):
        qs = SalaryStructure.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsHR]
    filterset_fields = ["salary_structure"]
    search_fields = ["employee__first_name", "employee__last_name"]

    def get_queryset(self):
        return EmployeeSalary.objects.select_related("employee", "salary_structure")


class PayslipViewSet(viewsets.ModelViewSet):
    serializer_class = PayslipSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ["employee", "school", "month", "year", "status"]

    def get_queryset(self):
        qs = Payslip.objects.select_related("employee")
        if self.request.user.role in ("teacher", "staff"):
            qs = qs.filter(employee=self.request.user)
        elif self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        payslip = self.get_object()
        payslip.status = "approved"
        payslip.approved_by = request.user
        payslip.save(update_fields=["status", "approved_by"])
        return Response({"detail": "Payslip approved."})

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        payslip = self.get_object()
        payslip.status = "paid"
        payslip.save(update_fields=["status"])
        return Response({"detail": "Payslip marked as paid."})


class PayrollRunViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ["school", "month", "year", "status"]

    def get_queryset(self):
        qs = PayrollRun.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(processed_by=self.request.user)
