from django.contrib import admin

from .models import Book, BookCategory, BookCopy, BookTransaction, LibraryMembership


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "parent")
    list_filter = ("school",)
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "total_copies", "available_copies", "is_active")
    list_filter = ("school", "category", "language", "is_active")
    search_fields = ("title", "isbn", "author")


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("book", "copy_number", "barcode", "condition", "is_available")
    list_filter = ("condition", "is_available")
    search_fields = ("barcode", "book__title")


@admin.register(BookTransaction)
class BookTransactionAdmin(admin.ModelAdmin):
    list_display = ("book_copy", "member", "transaction_type", "issue_date", "due_date", "return_date", "fine_amount")
    list_filter = ("transaction_type", "fine_paid")
    search_fields = ("book_copy__book__title", "member__first_name", "member__last_name")


@admin.register(LibraryMembership)
class LibraryMembershipAdmin(admin.ModelAdmin):
    list_display = ("membership_number", "user", "school", "membership_type", "max_books", "is_active")
    list_filter = ("school", "membership_type", "is_active")
    search_fields = ("membership_number", "user__first_name", "user__last_name")
