import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAccountant, IsSchoolAdmin

from .models import FeeCategory, FeeStructure, FeeWaiver, Invoice, InvoiceItem, Payment, Scholarship, StudentScholarship
from .serializers import (
    FeeCategorySerializer,
    FeeStructureSerializer,
    FeeWaiverSerializer,
    InvoiceListSerializer,
    InvoiceSerializer,
    PaymentSerializer,
    ScholarshipSerializer,
    StudentScholarshipSerializer,
)


class FeeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCategorySerializer
    permission_classes = [IsAccountant]
    filterset_fields = ["school", "is_active", "is_recurring"]

    def get_queryset(self):
        qs = FeeCategory.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class FeeStructureViewSet(viewsets.ModelViewSet):
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ["school", "academic_year", "class_obj", "category", "frequency"]

    def get_queryset(self):
        qs = FeeStructure.objects.select_related("class_obj", "category", "academic_year")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAccountant]
    filterset_fields = ["school", "student", "academic_year", "status"]
    search_fields = ["invoice_number", "student__student_id", "student__user__first_name"]
    ordering_fields = ["issue_date", "due_date", "total_amount"]

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        return InvoiceSerializer

    def get_queryset(self):
        qs = Invoice.objects.select_related("student__user", "academic_year").prefetch_related("items")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        inv_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        serializer.save(invoice_number=inv_number, generated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "issued"
        invoice.issue_date = timezone.now().date()
        invoice.save(update_fields=["status", "issue_date"])
        return Response({"detail": "Invoice issued."})


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ["school", "student", "invoice", "payment_method", "status"]
    search_fields = ["receipt_number", "transaction_id"]

    def get_queryset(self):
        qs = Payment.objects.select_related("student__user", "invoice")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        receipt = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        payment = serializer.save(receipt_number=receipt, received_by=self.request.user)
        # Update invoice paid amount
        invoice = payment.invoice
        invoice.paid_amount += payment.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = "paid"
        else:
            invoice.status = "partially_paid"
        invoice.save(update_fields=["paid_amount", "status"])

    @action(detail=False, methods=["post"])
    def create_stripe_intent(self, request):
        """Create a Stripe payment intent."""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        amount = request.data.get("amount")
        invoice_id = request.data.get("invoice_id")
        if not amount or not invoice_id:
            return Response({"detail": "amount and invoice_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),
                currency="usd",
                metadata={"invoice_id": str(invoice_id)},
            )
            return Response({"client_secret": intent.client_secret, "payment_intent_id": intent.id})
        except stripe.error.StripeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["school", "is_active", "discount_type"]
    search_fields = ["name"]

    def get_queryset(self):
        qs = Scholarship.objects.all()
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class StudentScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = StudentScholarshipSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["student", "scholarship", "academic_year", "is_active"]

    def get_queryset(self):
        return StudentScholarship.objects.select_related("student__user", "scholarship")

    def perform_create(self, serializer):
        serializer.save(approved_by=self.request.user)


class FeeWaiverViewSet(viewsets.ModelViewSet):
    serializer_class = FeeWaiverSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["student", "fee_category", "academic_year"]

    def get_queryset(self):
        return FeeWaiver.objects.select_related("student__user", "fee_category")

    def perform_create(self, serializer):
        serializer.save(approved_by=self.request.user)
