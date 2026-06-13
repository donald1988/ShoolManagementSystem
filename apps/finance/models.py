from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class FeeCategory(TimeStampedModel):
    """Categories of fees."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="fee_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "fee_categories"
        unique_together = [("school", "name")]
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return self.name


class FeeStructure(TimeStampedModel):
    """Fee structure definition per class and academic year."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="fee_structures")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="fee_structures")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="fee_structures")
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name="fee_structures")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ("one_time", "One Time"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("semi_annual", "Semi-Annual"),
            ("annual", "Annual"),
        ],
        default="annual",
    )
    due_day = models.PositiveSmallIntegerField(default=1, help_text="Day of month when fee is due")

    class Meta(TimeStampedModel.Meta):
        db_table = "fee_structures"
        unique_together = [("school", "academic_year", "class_obj", "category")]

    def __str__(self):
        return f"{self.class_obj.name} - {self.category.name}: {self.amount}"


class Invoice(TimeStampedModel):
    """Generated invoice for a student."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="invoices")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="invoices")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=30, unique=True, db_index=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="generated_invoices"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "invoices"

    def __str__(self):
        return f"INV-{self.invoice_number}"

    @property
    def balance(self):
        return self.total_amount - self.paid_amount


class InvoiceItem(TimeStampedModel):
    """Line items within an invoice."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta(TimeStampedModel.Meta):
        db_table = "invoice_items"

    def __str__(self):
        return f"{self.description}: {self.total}"

    def save(self, *args, **kwargs):
        self.total = self.amount * self.quantity
        super().save(*args, **kwargs)


class Payment(TimeStampedModel):
    """Payment records."""

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("ach", "ACH"),
        ("paypal", "PayPal"),
        ("stripe", "Stripe"),
        ("mobile_money", "Mobile Money"),
        ("check", "Check"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    receipt_number = models.CharField(max_length=30, blank=True, unique=True)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_payments"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "payments"

    def __str__(self):
        return f"Payment {self.receipt_number}: {self.amount}"


class Scholarship(TimeStampedModel):
    """Scholarship definitions."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="scholarships")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=15,
        choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")],
        default="percentage",
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    criteria = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "scholarships"

    def __str__(self):
        return self.name


class StudentScholarship(TimeStampedModel):
    """Scholarship assignments to students."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="scholarships")
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name="student_scholarships")
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="approved_scholarships"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "student_scholarships"
        unique_together = [("student", "scholarship", "academic_year")]

    def __str__(self):
        return f"{self.student} - {self.scholarship.name}"


class FeeWaiver(TimeStampedModel):
    """Fee waiver/discount for specific students."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="fee_waivers")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE)
    waiver_type = models.CharField(
        max_length=15,
        choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")],
        default="percentage",
    )
    waiver_value = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="approved_waivers"
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "fee_waivers"

    def __str__(self):
        return f"Waiver: {self.student} - {self.fee_category.name}"
