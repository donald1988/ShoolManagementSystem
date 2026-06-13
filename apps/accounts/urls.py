from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"roles", views.RoleViewSet, basename="role")
router.register(r"permissions", views.PermissionViewSet, basename="permission")
router.register(r"role-assignments", views.UserRoleAssignmentViewSet, basename="role-assignment")

urlpatterns = [
    # JWT endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Auth endpoints
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Router endpoints
    path("", include(router.urls)),
]
