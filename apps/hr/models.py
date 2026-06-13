from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Employee(TimeStampedModel):
    """Employee record linked to a user account."""

    CONTRACT_TYPES = [
        ("permanent", "Permanent"),
        ("contract", "Contract"),
        ("part_time", "Part Time"),
        ("intern", "Intern"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile"
    )
    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="employees"
    )
    employee_id = models.CharField(max_length=50)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, default="permanent")
    salary = models.ForeignKey(
        "payroll.EmployeeSalary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr_employee",
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_employees"
        unique_together = [("school", "employee_id")]

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class EmployeeContract(TimeStampedModel):
    """Contract details for an employee."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contracts")
    contract_type = models.CharField(max_length=20, choices=Employee.CONTRACT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to="hr/contracts/", blank=True)
    terms = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_employee_contracts"

    def __str__(self):
        return f"{self.employee} - {self.contract_type} ({self.start_date})"


class LeaveType(TimeStampedModel):
    """Types of leave available."""

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="leave_types"
    )
    name = models.CharField(max_length=100)
    max_days_per_year = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_leave_types"
        unique_together = [("school", "name")]

    def __str__(self):
        return self.name


class LeaveRequest(TimeStampedModel):
    """Employee leave request."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests"
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="requests")
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_leave_requests"

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"


class PerformanceReview(TimeStampedModel):
    """Employee performance review."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="performance_reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="given_reviews"
    )
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE, related_name="performance_reviews"
    )
    review_period = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_performance_reviews"

    def __str__(self):
        return f"Review: {self.employee} by {self.reviewer} ({self.review_period})"


class Recruitment(TimeStampedModel):
    """Job posting for recruitment."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("on_hold", "On Hold"),
    ]

    school = models.ForeignKey(
        "core.School", on_delete=models.CASCADE, related_name="recruitments"
    )
    position = models.CharField(max_length=100)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recruitments",
    )
    description = models.TextField()
    requirements = models.TextField()
    num_positions = models.PositiveIntegerField(default=1)
    application_deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_recruitments",
    )

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_recruitments"

    def __str__(self):
        return f"{self.position} ({self.school})"


class JobApplication(TimeStampedModel):
    """Application for a recruitment posting."""

    STATUS_CHOICES = [
        ("received", "Received"),
        ("shortlisted", "Shortlisted"),
        ("interviewed", "Interviewed"),
        ("offered", "Offered"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]

    recruitment = models.ForeignKey(
        Recruitment, on_delete=models.CASCADE, related_name="applications"
    )
    applicant_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to="hr/resumes/")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")

    class Meta(TimeStampedModel.Meta):
        db_table = "hr_job_applications"

    def __str__(self):
        return f"{self.applicant_name} - {self.recruitment.position}"
