from django.contrib import admin
from .models import FeeCategory, FeeStructure, FeeWaiver, Invoice, InvoiceItem, Payment, Scholarship, StudentScholarship


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "is_recurring", "is_active")


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "category", "amount", "frequency", "academic_year")
    list_filter = ("academic_year", "frequency")


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student", "total_amount", "paid_amount", "status", "due_date")
    list_filter = ("status", "academic_year")
    search_fields = ("invoice_number", "student__student_id")
    inlines = [InvoiceItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "student", "amount", "payment_method", "status", "payment_date")
    list_filter = ("payment_method", "status")
    search_fields = ("receipt_number", "transaction_id")


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "discount_type", "discount_value", "is_active")


@admin.register(StudentScholarship)
class StudentScholarshipAdmin(admin.ModelAdmin):
    list_display = ("student", "scholarship", "academic_year", "is_active")


@admin.register(FeeWaiver)
class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_category", "waiver_type", "waiver_value", "academic_year")
