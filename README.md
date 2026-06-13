# School Management System (SMS)

Enterprise-grade, production-ready School Management System built with Django REST Framework and PostgreSQL. Supports K-12 schools, colleges, universities, training centers, and multi-campus educational institutions.

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 / Django 5.1 / DRF 3.15 |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Task Queue | Celery 5 |
| Auth | JWT (Simple JWT) |
| Payments | Stripe |
| Docs | OpenAPI 3 (drf-spectacular) |
| Container | Docker / Docker Compose |

## Modules (21 Django Apps)

| App | Description |
|-----|-------------|
| `core` | Schools, Campuses, Academic Years, Terms, System Config |
| `accounts` | Users, Roles, Permissions, JWT Auth, RBAC |
| `students` | Student profiles, Parents, Documents, Promotions |
| `admissions` | Online applications, Workflow, Seat management |
| `academics` | Departments, Classes, Sections, Subjects, Enrollments, Teachers |
| `attendance` | Student & Teacher attendance, Period-wise, Bulk marking |
| `examinations` | Exams, Grading, Report Cards, GPA calculation |
| `lms` | Courses, Lessons, Assignments, Live classes, Forums |
| `finance` | Fees, Invoices, Payments, Scholarships, Stripe integration |
| `payroll` | Salary structures, Payslips, Payroll runs |
| `hr` | Employees, Contracts, Leave management, Recruitment |
| `communication` | Messages, Announcements, Notifications, Emergency alerts |
| `timetable` | Scheduling, Rooms, Periods, Conflict detection |
| `library` | Books, Circulation, Memberships, Fines |
| `transport` | Vehicles, Routes, GPS tracking, Student transport |
| `hostel` | Buildings, Rooms, Beds, Allocations |
| `inventory` | Assets, Maintenance, Transfers |
| `health` | Medical records, Vaccinations, Health visits |
| `discipline` | Incidents, Detentions, Suspensions, Behavior points |
| `analytics` | Dashboards, Reports, AI predictions |
| `audit` | Audit logs, Login attempts, Data export logs |

## User Roles

Super Admin, School Admin, Principal, Teacher, Student, Parent, Accountant, Librarian, HR, Transport Manager, Nurse, Staff

## Quick Start

### Using Docker (Recommended)

```bash
# Clone and navigate to project
cp .env.example .env
# Edit .env with your settings

docker compose up -d
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_permissions
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL must be running)
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Seed permissions
python manage.py seed_permissions

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Start Celery (for async tasks)

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

All endpoints are under `/api/v1/`:

```
/api/v1/auth/token/                  # JWT login
/api/v1/auth/token/refresh/          # Refresh token
/api/v1/auth/register/               # Register user
/api/v1/auth/profile/                # User profile
/api/v1/core/schools/                # Schools CRUD
/api/v1/core/academic-years/         # Academic years
/api/v1/students/students/           # Students
/api/v1/admissions/applications/     # Admission applications
/api/v1/academics/classes/           # Classes
/api/v1/attendance/student/          # Student attendance
/api/v1/examinations/exams/          # Examinations
/api/v1/lms/courses/                 # LMS courses
/api/v1/finance/invoices/            # Invoices
/api/v1/finance/payments/            # Payments
/api/v1/payroll/payslips/            # Payslips
/api/v1/hr/leave-requests/           # Leave requests
/api/v1/communication/messages/      # Messages
/api/v1/timetable/entries/           # Timetable
/api/v1/library/books/               # Library books
/api/v1/transport/routes/            # Bus routes
/api/v1/hostel/rooms/                # Hostel rooms
/api/v1/inventory/assets/            # Assets
/api/v1/health/medical-records/      # Medical records
/api/v1/discipline/incidents/        # Discipline incidents
/api/v1/analytics/reports/           # Reports
/api/v1/audit/logs/                  # Audit logs
```

## Security Features

- JWT authentication with token blacklisting
- Role-based access control (RBAC)
- Object-level permissions (django-guardian)
- Rate limiting / throttling
- CORS configuration
- Audit logging
- Password validation (min 10 chars)
- HTTPS enforcement in production
- HSTS headers
- XSS / CSRF protection
- Content-Type nosniff

## Testing

```bash
pytest
pytest --cov=apps --cov-report=html
```

## Production Deployment

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production`
2. Configure all secrets in `.env`
3. Set up PostgreSQL and Redis
4. Run `python manage.py migrate`
5. Run `python manage.py collectstatic`
6. Deploy with Gunicorn behind Nginx
7. Configure SSL/TLS certificates
8. Set up Celery workers and beat scheduler
9. Configure Sentry for error monitoring
