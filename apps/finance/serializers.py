from rest_framework import serializers
from .models import FeeCategory, FeeStructure, FeeWaiver, Invoice, InvoiceItem, Payment, Scholarship, StudentScholarship


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FeeStructureSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)

    class Meta:
        model = FeeStructure
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "total")


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "generated_by")


class InvoiceListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = (
            "id", "invoice_number", "student_name", "issue_date",
            "due_date", "total_amount", "paid_amount", "balance", "status",
        )


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "received_by")


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StudentScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    scholarship_name = serializers.CharField(source="scholarship.name", read_only=True)

    class Meta:
        model = StudentScholarship
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FeeWaiverSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = FeeWaiver
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
