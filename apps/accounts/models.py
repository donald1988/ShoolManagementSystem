import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "super_admin")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model supporting all stakeholder roles."""

    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("school_admin", "School Admin"),
        ("principal", "Principal"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("parent", "Parent"),
        ("accountant", "Accountant"),
        ("librarian", "Librarian"),
        ("hr", "HR"),
        ("transport_manager", "Transport Manager"),
        ("nurse", "Nurse"),
        ("staff", "Staff"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    school = models.ForeignKey(
        "core.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Role(TimeStampedModel):
    """Custom role definitions with granular permissions."""

    school = models.ForeignKey("core.School", on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField("Permission", blank=True, related_name="roles")
    is_system = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        db_table = "custom_roles"
        unique_together = [("school", "name")]

    def __str__(self):
        return self.name


class Permission(TimeStampedModel):
    """Granular permission definitions."""

    MODULE_CHOICES = [
        ("students", "Students"),
        ("admissions", "Admissions"),
        ("academics", "Academics"),
        ("attendance", "Attendance"),
        ("examinations", "Examinations"),
        ("lms", "LMS"),
        ("finance", "Finance"),
        ("payroll", "Payroll"),
        ("hr", "HR"),
        ("communication", "Communication"),
        ("timetable", "Timetable"),
        ("library", "Library"),
        ("transport", "Transport"),
        ("hostel", "Hostel"),
        ("inventory", "Inventory"),
        ("health", "Health"),
        ("discipline", "Discipline"),
        ("analytics", "Analytics"),
        ("settings", "Settings"),
    ]

    ACTION_CHOICES = [
        ("create", "Create"),
        ("read", "Read"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("export", "Export"),
        ("import", "Import"),
        ("approve", "Approve"),
    ]

    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    class Meta(TimeStampedModel.Meta):
        db_table = "custom_permissions"
        ordering = ["module", "action"]

    def __str__(self):
        return self.codename


class UserRoleAssignment(TimeStampedModel):
    """Assigns custom roles to users for fine-grained access control."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_assignments")

    class Meta(TimeStampedModel.Meta):
        db_table = "user_role_assignments"
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
