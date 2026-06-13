from rest_framework import serializers

from .models import Book, BookCategory, BookCopy, BookTransaction, LibraryMembership


class BookCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True, default=None)

    class Meta:
        model = BookCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BookCopySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BookCopy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BookTransactionSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book_copy.book.title", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.full_name", read_only=True)

    class Meta:
        model = BookTransaction
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class LibraryMembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = LibraryMembership
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
