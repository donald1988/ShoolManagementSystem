from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class SalaryStructure(TimeStampedModel):
    """Salary structure template."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="salary_structures")
    name = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pension_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "salary_structures"

    def __str__(self):
        return self.name

    @property
    def gross_salary(self):
        return (
            self.base_salary
            + self.housing_allowance
            + self.transport_allowance
            + self.medical_allowance
            + self.other_allowances
        )

    @property
    def total_deductions(self):
        tax = self.gross_salary * (self.tax_percentage / 100)
        pension = self.gross_salary * (self.pension_percentage / 100)
        return tax + pension + self.insurance_deduction

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions


class EmployeeSalary(TimeStampedModel):
    """Employee salary assignment."""

    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="salary")
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, related_name="employees")
    custom_base_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_routing_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "employee_salaries"
        verbose_name_plural = "Employee Salaries"

    def __str__(self):
        return f"{self.employee.full_name} - {self.salary_structure.name}"


class Payslip(TimeStampedModel):
    """Monthly payslip for employees."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payslips")
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="payslips")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pension_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="draft")
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_payslips"
    )
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "payslips"
        unique_together = [("employee", "month", "year")]

    def __str__(self):
        return f"Payslip: {self.employee.full_name} - {self.month}/{self.year}"


class PayrollRun(TimeStampedModel):
    """Batch payroll processing run."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="payroll_runs")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    total_employees = models.PositiveIntegerField(default=0)
    total_gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=15,
        choices=[
            ("draft", "Draft"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="payroll_runs"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "payroll_runs"
        unique_together = [("school", "month", "year")]

    def __str__(self):
        return f"Payroll Run: {self.month}/{self.year}"
