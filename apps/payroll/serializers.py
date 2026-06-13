from rest_framework import serializers
from .models import EmployeeSalary, PayrollRun, Payslip, SalaryStructure


class SalaryStructureSerializer(serializers.ModelSerializer):
    gross_salary = serializers.ReadOnlyField()
    total_deductions = serializers.ReadOnlyField()
    net_salary = serializers.ReadOnlyField()

    class Meta:
        model = SalaryStructure
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    structure_name = serializers.CharField(source="salary_structure.name", read_only=True)

    class Meta:
        model = EmployeeSalary
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = Payslip
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
