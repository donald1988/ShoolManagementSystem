from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class BookCategory(TimeStampedModel):
    """Category/genre for books with optional hierarchy."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="book_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")

    class Meta(TimeStampedModel.Meta):
        db_table = "book_categories"
        unique_together = [("school", "name")]
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return self.name


class Book(TimeStampedModel):
    """Library book record."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="library_books")
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    publish_year = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    edition = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default="English")
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to="library/covers/", blank=True)
    location = models.CharField(max_length=100, blank=True, help_text="Shelf location")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "library_books"

    def __str__(self):
        return f"{self.title} by {self.author}"


class BookCopy(TimeStampedModel):
    """Individual physical copy of a book."""

    CONDITION_CHOICES = [
        ("new", "New"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
        ("damaged", "Damaged"),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    copy_number = models.CharField(max_length=20)
    barcode = models.CharField(max_length=50, unique=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default="new")
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "book_copies"
        verbose_name_plural = "Book Copies"

    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number}"


class BookTransaction(TimeStampedModel):
    """Record of book issue, return, renewal, or loss."""

    TRANSACTION_TYPES = [
        ("issue", "Issue"),
        ("return", "Return"),
        ("renew", "Renew"),
        ("lost", "Lost"),
    ]

    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name="transactions")
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_transactions"
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="books_issued"
    )
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "book_transactions"

    def __str__(self):
        return f"{self.transaction_type} - {self.book_copy} - {self.member}"


class LibraryMembership(TimeStampedModel):
    """Library membership for users."""

    MEMBERSHIP_TYPES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("staff", "Staff"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="library_membership"
    )
    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="library_memberships")
    membership_number = models.CharField(max_length=50, unique=True)
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_TYPES)
    max_books = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "library_memberships"

    def __str__(self):
        return f"{self.membership_number} - {self.user}"
