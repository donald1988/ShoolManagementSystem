from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "super_admin"


class IsSchoolAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("super_admin", "school_admin")


class IsPrincipal(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("super_admin", "school_admin", "principal")


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "super_admin",
            "school_admin",
            "principal",
            "teacher",
        )


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "parent"


class IsAccountant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("super_admin", "school_admin", "accountant")


class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("super_admin", "school_admin", "librarian")


class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("super_admin", "school_admin", "hr")


class IsTransportManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "super_admin",
            "school_admin",
            "transport_manager",
        )


class IsSchoolMember(permissions.BasePermission):
    """Ensure user belongs to the school they're accessing."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "super_admin":
            return True
        school_id = view.kwargs.get("school_id") or request.query_params.get("school")
        if school_id and request.user.school_id:
            return str(request.user.school_id) == str(school_id)
        return True


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
