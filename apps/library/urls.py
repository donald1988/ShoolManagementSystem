from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"categories", views.BookCategoryViewSet, basename="book-category")
router.register(r"books", views.BookViewSet, basename="book")
router.register(r"copies", views.BookCopyViewSet, basename="book-copy")
router.register(r"transactions", views.BookTransactionViewSet, basename="book-transaction")
router.register(r"memberships", views.LibraryMembershipViewSet, basename="library-membership")

urlpatterns = [
    path("", include(router.urls)),
]
