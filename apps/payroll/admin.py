from django.contrib import admin
from .models import EmployeeSalary, PayrollRun, Payslip, SalaryStructure


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "base_salary", "is_active")


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ("employee", "salary_structure")
    search_fields = ("employee__first_name", "employee__last_name")


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "year", "gross_salary", "net_salary", "status")
    list_filter = ("status", "month", "year")


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ("school", "month", "year", "total_employees", "total_net", "status")
    list_filter = ("status", "year")
