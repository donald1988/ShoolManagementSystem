from datetime import date, timedelta

from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsLibrarian

from .models import Book, BookCategory, BookCopy, BookTransaction, LibraryMembership
from .serializers import (
    BookCategorySerializer,
    BookCopySerializer,
    BookSerializer,
    BookTransactionSerializer,
    LibraryMembershipSerializer,
)


class BookCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BookCategorySerializer
    permission_classes = [IsLibrarian]
    filterset_fields = ["school", "parent"]
    search_fields = ["name"]

    def get_queryset(self):
        qs = BookCategory.objects.select_related("parent")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    filterset_fields = ["school", "category", "language", "is_active"]
    search_fields = ["title", "isbn", "author"]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "search"):
            return [IsAuthenticated()]
        return [IsLibrarian()]

    def get_queryset(self):
        qs = Book.objects.select_related("category")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Public book search endpoint."""
        query = request.query_params.get("q", "")
        if not query:
            return Response({"error": "Search query 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        books = self.get_queryset().filter(
            models.Q(title__icontains=query)
            | models.Q(author__icontains=query)
            | models.Q(isbn__icontains=query),
            is_active=True,
        )
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


class BookCopyViewSet(viewsets.ModelViewSet):
    serializer_class = BookCopySerializer
    permission_classes = [IsLibrarian]
    filterset_fields = ["book", "condition", "is_available"]

    def get_queryset(self):
        return BookCopy.objects.select_related("book")


class BookTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = BookTransactionSerializer
    permission_classes = [IsLibrarian]
    filterset_fields = ["book_copy", "member", "transaction_type"]

    def get_queryset(self):
        return BookTransaction.objects.select_related("book_copy__book", "member", "issued_by")

    @action(detail=False, methods=["post"], url_path="issue-book")
    def issue_book(self, request):
        """Issue a book to a member."""
        book_copy_id = request.data.get("book_copy_id")
        member_id = request.data.get("member_id")
        due_days = int(request.data.get("due_days", 14))

        if not book_copy_id or not member_id:
            return Response(
                {"error": "book_copy_id and member_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book_copy = BookCopy.objects.get(id=book_copy_id)
        except BookCopy.DoesNotExist:
            return Response({"error": "Book copy not found"}, status=status.HTTP_404_NOT_FOUND)

        if not book_copy.is_available:
            return Response({"error": "Book copy is not available"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = BookTransaction.objects.create(
            book_copy=book_copy,
            member_id=member_id,
            transaction_type="issue",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=due_days),
            issued_by=request.user,
        )
        book_copy.is_available = False
        book_copy.save(update_fields=["is_available"])
        book_copy.book.available_copies = max(0, book_copy.book.available_copies - 1)
        book_copy.book.save(update_fields=["available_copies"])

        return Response(BookTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="return-book")
    def return_book(self, request):
        """Return a book from a member."""
        book_copy_id = request.data.get("book_copy_id")
        fine_amount = request.data.get("fine_amount", 0)

        if not book_copy_id:
            return Response({"error": "book_copy_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = (
            BookTransaction.objects.filter(
                book_copy_id=book_copy_id, transaction_type="issue", return_date__isnull=True
            )
            .order_by("-issue_date")
            .first()
        )
        if not transaction:
            return Response({"error": "No active issue found for this book copy"}, status=status.HTTP_404_NOT_FOUND)

        transaction.return_date = date.today()
        transaction.transaction_type = "return"
        transaction.fine_amount = fine_amount
        transaction.save(update_fields=["return_date", "transaction_type", "fine_amount"])

        book_copy = transaction.book_copy
        book_copy.is_available = True
        book_copy.save(update_fields=["is_available"])
        book_copy.book.available_copies += 1
        book_copy.book.save(update_fields=["available_copies"])

        return Response(BookTransactionSerializer(transaction).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        """Renew a book transaction."""
        transaction = self.get_object()
        extend_days = int(request.data.get("extend_days", 14))

        if transaction.return_date is not None:
            return Response({"error": "Book has already been returned"}, status=status.HTTP_400_BAD_REQUEST)

        transaction.due_date = transaction.due_date + timedelta(days=extend_days)
        transaction.transaction_type = "renew"
        transaction.save(update_fields=["due_date", "transaction_type"])

        return Response(BookTransactionSerializer(transaction).data)


class LibraryMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryMembershipSerializer
    permission_classes = [IsLibrarian]
    filterset_fields = ["school", "membership_type", "is_active"]
    search_fields = ["membership_number", "user__first_name", "user__last_name"]

    def get_queryset(self):
        qs = LibraryMembership.objects.select_related("user")
        if self.request.user.role != "super_admin" and self.request.user.school_id:
            qs = qs.filter(school_id=self.request.user.school_id)
        return qs
