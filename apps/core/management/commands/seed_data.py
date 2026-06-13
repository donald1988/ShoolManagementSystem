"""
Management command to seed the database with realistic sample data.
Usage: python manage.py seed_data
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seeds the database with sample data for all modules"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Clear existing data before seeding")

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        from apps.accounts.models import User
        from apps.core.models import AcademicYear, Campus, School, Term

        # ── School ──
        school, _ = School.objects.get_or_create(
            code="SMS001",
            defaults=dict(
                name="Springfield International Academy",
                email="info@springfield.edu",
                phone="+1-555-0100",
                website="https://springfield.edu",
                address_line1="123 Education Lane",
                city="Springfield",
                state="Illinois",
                postal_code="62701",
                country="US",
            ),
        )
        self.stdout.write(self.style.SUCCESS(f"  School: {school.name}"))

        # ── Campuses ──
        campuses_data = [
            ("Main Campus", "MAIN", "123 Education Lane", True),
            ("East Campus", "EAST", "456 Learning Drive", False),
        ]
        campuses = []
        for name, code, addr, is_main in campuses_data:
            c, _ = Campus.objects.get_or_create(
                code=code, school=school,
                defaults=dict(name=name, address_line1=addr, city="Springfield", state="Illinois",
                              postal_code="62701", is_main=is_main),
            )
            campuses.append(c)
        self.stdout.write(self.style.SUCCESS(f"  Campuses: {len(campuses)}"))

        # ── Academic Year & Terms ──
        ay, _ = AcademicYear.objects.get_or_create(
            name="2025-2026", school=school,
            defaults=dict(start_date=date(2025, 9, 1), end_date=date(2026, 6, 30), is_current=True),
        )
        terms_data = [
            ("Fall 2025", date(2025, 9, 1), date(2025, 12, 20), 1),
            ("Spring 2026", date(2026, 1, 10), date(2026, 3, 31), 2),
            ("Summer 2026", date(2026, 4, 7), date(2026, 6, 30), 3),
        ]
        terms = []
        for name, start, end, order in terms_data:
            t, _ = Term.objects.get_or_create(
                name=name, academic_year=ay,
                defaults=dict(start_date=start, end_date=end, order=order, is_current=(order == 2)),
            )
            terms.append(t)

        # ── Assign superadmin to school ──
        superadmin = User.objects.filter(is_superuser=True).first()
        if superadmin and not superadmin.school:
            superadmin.school = school
            superadmin.role = "super_admin"
            superadmin.save()

        # ── Staff Users ──
        staff_data = [
            ("principal@springfield.edu", "James", "Wilson", "principal"),
            ("admin@springfield.edu", "Sarah", "Johnson", "school_admin"),
            ("teacher1@springfield.edu", "Michael", "Brown", "teacher"),
            ("teacher2@springfield.edu", "Emily", "Davis", "teacher"),
            ("teacher3@springfield.edu", "Robert", "Martinez", "teacher"),
            ("teacher4@springfield.edu", "Lisa", "Anderson", "teacher"),
            ("teacher5@springfield.edu", "David", "Taylor", "teacher"),
            ("teacher6@springfield.edu", "Jennifer", "Thomas", "teacher"),
            ("accountant@springfield.edu", "William", "Moore", "accountant"),
            ("librarian@springfield.edu", "Patricia", "White", "librarian"),
            ("hr@springfield.edu", "Richard", "Harris", "hr"),
            ("transport@springfield.edu", "Charles", "Clark", "transport_manager"),
            ("nurse@springfield.edu", "Maria", "Lewis", "nurse"),
        ]
        staff_users = {}
        for email, first, last, role in staff_data:
            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(first_name=first, last_name=last, role=role, school=school,
                              is_staff=(role in ("principal", "school_admin")),
                              is_active=True),
            )
            if created:
                u.set_password("password123")
                u.save()
            staff_users[role] = u
            if role.startswith("teacher"):
                staff_users.setdefault("teachers", [])
                staff_users["teachers"].append(u)

        teachers = staff_users.get("teachers", [])
        self.stdout.write(self.style.SUCCESS(f"  Staff users: {len(staff_data)}"))

        # ── Departments ──
        from apps.academics.models import Class, ClassSubject, Department, Section, Subject, Teacher

        depts_data = ["Mathematics", "Science", "English", "Social Studies", "Arts", "Physical Education"]
        departments = []
        for i, name in enumerate(depts_data):
            d, _ = Department.objects.get_or_create(
                name=name, school=school,
                defaults=dict(code=name[:4].upper(), head=teachers[i] if i < len(teachers) else None),
            )
            departments.append(d)

        # ── Classes & Sections ──
        classes_data = [
            ("Grade 1", "G1", 1), ("Grade 2", "G2", 2), ("Grade 3", "G3", 3),
            ("Grade 4", "G4", 4), ("Grade 5", "G5", 5), ("Grade 6", "G6", 6),
            ("Grade 7", "G7", 7), ("Grade 8", "G8", 8), ("Grade 9", "G9", 9),
            ("Grade 10", "G10", 10),
        ]
        classes = []
        sections_map = {}
        for name, code, level in classes_data:
            cls, _ = Class.objects.get_or_create(
                code=code, school=school,
                defaults=dict(name=name, numeric_level=level),
            )
            classes.append(cls)
            secs = []
            for sec_name in ["A", "B"]:
                teacher_idx = (level - 1) * 2 + (0 if sec_name == "A" else 1)
                sec, _ = Section.objects.get_or_create(
                    name=sec_name, class_obj=cls,
                    defaults=dict(class_teacher=teachers[teacher_idx % len(teachers)] if teachers else None),
                )
                secs.append(sec)
            sections_map[cls.id] = secs

        # ── Subjects ──
        subjects_data = [
            ("Mathematics", "MATH", 0), ("Physics", "PHY", 1), ("Chemistry", "CHEM", 1),
            ("Biology", "BIO", 1), ("English", "ENG", 2), ("Literature", "LIT", 2),
            ("History", "HIST", 3), ("Geography", "GEO", 3), ("Art", "ART", 4),
            ("Music", "MUS", 4), ("Physical Education", "PE", 5), ("Computer Science", "CS", 0),
        ]
        subjects = []
        for name, code, dept_idx in subjects_data:
            s, _ = Subject.objects.get_or_create(
                code=code, school=school,
                defaults=dict(name=name, department=departments[dept_idx]),
            )
            subjects.append(s)

        # ── Teachers (academic profile) ──
        teacher_profiles = []
        for i, user in enumerate(teachers):
            tp, _ = Teacher.objects.get_or_create(
                user=user,
                defaults=dict(employee_id=f"T{i+1:04d}", school=school,
                              department=departments[i % len(departments)]),
            )
            teacher_profiles.append(tp)

        # ── Class-Subject assignments ──
        for cls in classes:
            for j, subj in enumerate(subjects[:8]):  # assign first 8 subjects
                ClassSubject.objects.get_or_create(
                    class_obj=cls, subject=subj, academic_year=ay,
                    defaults=dict(teacher=teachers[j % len(teachers)]),
                )

        self.stdout.write(self.style.SUCCESS(
            f"  Academics: {len(departments)} depts, {len(classes)} classes, {len(subjects)} subjects"
        ))

        # ── Students (60 students across grades) ──
        from apps.students.models import EmergencyContact, Parent, Student, StudentParent

        first_names_m = ["Liam", "Noah", "Oliver", "Ethan", "Aiden", "Lucas", "Mason", "Logan",
                         "James", "Benjamin", "Henry", "Alexander", "Sebastian", "Jack", "Daniel"]
        first_names_f = ["Emma", "Olivia", "Ava", "Sophia", "Isabella", "Mia", "Charlotte",
                         "Amelia", "Harper", "Evelyn", "Abigail", "Emily", "Ella", "Lily", "Grace"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                      "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
                      "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

        students = []
        student_users = []
        for i in range(60):
            is_female = i % 2 == 1
            first = (first_names_f if is_female else first_names_m)[i % 15]
            last = last_names[i % len(last_names)]
            email = f"student{i+1}@springfield.edu"

            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(first_name=first, last_name=last, role="student",
                              school=school, is_active=True),
            )
            if created:
                u.set_password("password123")
                u.save()
            student_users.append(u)

            cls = classes[i % len(classes)]
            secs = sections_map.get(cls.id, [])
            sec = secs[i % 2] if secs else None

            st, _ = Student.objects.get_or_create(
                user=u,
                defaults=dict(
                    school=school,
                    student_id=f"STU{i+1:04d}",
                    admission_number=f"ADM{2025}{i+1:04d}",
                    admission_date=date(2025, 8, 15),
                    date_of_birth=date(2010 + (i % 8), (i % 12) + 1, (i % 28) + 1),
                    gender="female" if is_female else "male",
                    blood_group=random.choice(["A+", "B+", "O+", "AB+"]),
                    current_class=cls,
                    current_section=sec,
                    status="enrolled",
                    city="Springfield", state="Illinois",
                    address_line1=f"{100 + i} Student Street",
                ),
            )
            students.append(st)

        # ── Parents (30 parents, 2 students each) ──
        parents = []
        for i in range(30):
            email = f"parent{i+1}@email.com"
            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(first_name=f"Parent{i+1}", last_name=last_names[i % len(last_names)],
                              role="parent", school=school, is_active=True,
                              phone=f"+1-555-{1000 + i}"),
            )
            if created:
                u.set_password("password123")
                u.save()

            p, _ = Parent.objects.get_or_create(user=u, defaults=dict(school=school))
            parents.append(p)

            # link 2 students per parent
            for j in [i * 2, i * 2 + 1]:
                if j < len(students):
                    StudentParent.objects.get_or_create(
                        student=students[j], parent=p,
                        defaults=dict(relationship="father" if i % 2 == 0 else "mother"),
                    )

            # Emergency contact
            if i * 2 < len(students):
                EmergencyContact.objects.get_or_create(
                    student=students[i * 2],
                    name=f"{u.first_name} {u.last_name}",
                    defaults=dict(relationship="Parent", phone=f"+1-555-{2000 + i}"),
                )

        self.stdout.write(self.style.SUCCESS(f"  Students: {len(students)}, Parents: {len(parents)}"))

        # ── Enrollments ──
        from apps.academics.models import Enrollment

        for st in students:
            if st.current_class:
                Enrollment.objects.get_or_create(
                    student=st, academic_year=ay, class_obj=st.current_class,
                    defaults=dict(section=st.current_section, is_active=True),
                )

        # ── Attendance (last 30 days) ──
        from apps.attendance.models import StudentAttendance

        statuses = ["present", "present", "present", "present", "absent", "late"]
        today = date.today()
        attendance_count = 0
        for day_offset in range(30):
            d = today - timedelta(days=day_offset)
            if d.weekday() >= 5:  # skip weekends
                continue
            for st in students[:20]:  # first 20 students for perf
                _, created = StudentAttendance.objects.get_or_create(
                    student=st, date=d, academic_year=ay,
                    defaults=dict(
                        class_obj=st.current_class or classes[0],
                        section=st.current_section,
                        status=random.choice(statuses),
                        marked_by=teachers[0] if teachers else None,
                    ),
                )
                if created:
                    attendance_count += 1

        self.stdout.write(self.style.SUCCESS(f"  Attendance records: {attendance_count}"))

        # ── Examinations ──
        from apps.examinations.models import Exam, ExamSchedule, ExamType, Grade, GradingScale, GradeRange

        exam_type, _ = ExamType.objects.get_or_create(name="Mid-Term", defaults=dict(school=school))
        exam_type2, _ = ExamType.objects.get_or_create(name="Final", defaults=dict(school=school))

        exam, _ = Exam.objects.get_or_create(
            name="Mid-Term Exam Fall 2025", school=school,
            defaults=dict(academic_year=ay, term=terms[0], exam_type=exam_type,
                          start_date=date(2025, 11, 1), end_date=date(2025, 11, 15)),
        )

        # Grading scale
        gs, _ = GradingScale.objects.get_or_create(name="Standard Grading", defaults=dict(school=school))
        grade_ranges = [
            ("A+", 95, 100, 4.0), ("A", 90, 94, 3.7), ("B+", 85, 89, 3.3),
            ("B", 80, 84, 3.0), ("C+", 75, 79, 2.7), ("C", 70, 74, 2.3),
            ("D", 60, 69, 1.0), ("F", 0, 59, 0.0),
        ]
        for letter, mn, mx, gp in grade_ranges:
            GradeRange.objects.get_or_create(
                grading_scale=gs, letter=letter,
                defaults=dict(min_percentage=mn, max_percentage=mx, grade_point=Decimal(str(gp))),
            )

        # Exam schedules & grades
        grade_count = 0
        for cls in classes[:5]:
            for subj in subjects[:4]:
                sched, _ = ExamSchedule.objects.get_or_create(
                    exam=exam, class_obj=cls, subject=subj,
                    defaults=dict(date=date(2025, 11, 5), start_time=time(9, 0),
                                  end_time=time(11, 0), max_marks=100),
                )
                cls_students = [s for s in students if s.current_class == cls]
                for st in cls_students:
                    _, created = Grade.objects.get_or_create(
                        student=st, exam_schedule=sched,
                        defaults=dict(marks_obtained=Decimal(str(random.randint(45, 98))),
                                      graded_by=teachers[0] if teachers else None),
                    )
                    if created:
                        grade_count += 1

        self.stdout.write(self.style.SUCCESS(f"  Exams: 2 types, {grade_count} grades"))

        # ── Finance ──
        from apps.finance.models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment

        fee_cats = []
        for name in ["Tuition Fee", "Lab Fee", "Library Fee", "Sports Fee", "Transport Fee"]:
            fc, _ = FeeCategory.objects.get_or_create(name=name, defaults=dict(school=school))
            fee_cats.append(fc)

        amounts = [Decimal("5000"), Decimal("500"), Decimal("300"), Decimal("400"), Decimal("800")]
        for cls in classes:
            for fc, amt in zip(fee_cats, amounts):
                FeeStructure.objects.get_or_create(
                    school=school, academic_year=ay, class_obj=cls, category=fc,
                    defaults=dict(amount=amt),
                )

        # Invoices for first 20 students
        invoice_count = 0
        for i, st in enumerate(students[:20]):
            inv, created = Invoice.objects.get_or_create(
                invoice_number=f"INV-2025-{i+1:04d}", school=school,
                defaults=dict(student=st, academic_year=ay,
                              issue_date=date(2025, 9, 1), due_date=date(2025, 10, 1),
                              total_amount=Decimal("7000"), status="paid" if i < 15 else "pending"),
            )
            if created:
                invoice_count += 1
                InvoiceItem.objects.get_or_create(
                    invoice=inv, fee_category=fee_cats[0],
                    defaults=dict(description="Tuition Fee - Fall 2025",
                                  amount=Decimal("5000"), quantity=1, total=Decimal("5000")),
                )
                InvoiceItem.objects.get_or_create(
                    invoice=inv, fee_category=fee_cats[1],
                    defaults=dict(description="Lab Fee", amount=Decimal("500"),
                                  quantity=1, total=Decimal("500")),
                )
                if inv.status == "paid":
                    Payment.objects.get_or_create(
                        invoice=inv, school=school,
                        defaults=dict(student=st, amount=Decimal("7000"),
                                      payment_method="bank_transfer",
                                      payment_date=timezone.make_aware(timezone.datetime(2025, 9, 15, 10, 0)),
                                      status="completed", transaction_id=f"TXN{i+1:06d}",
                                      receipt_number=f"RCP-2025-{i+1:04d}"),
                    )

        self.stdout.write(self.style.SUCCESS(f"  Invoices: {invoice_count}"))

        # ── Payroll ──
        from apps.payroll.models import SalaryStructure, EmployeeSalary, Payslip

        ss, _ = SalaryStructure.objects.get_or_create(
            name="Teaching Staff", school=school,
            defaults=dict(base_salary=Decimal("4500")),
        )
        ss2, _ = SalaryStructure.objects.get_or_create(
            name="Admin Staff", school=school,
            defaults=dict(base_salary=Decimal("3500")),
        )

        for user in teachers:
            es, _ = EmployeeSalary.objects.get_or_create(
                employee=user, defaults=dict(salary_structure=ss),
            )
            Payslip.objects.get_or_create(
                employee=user, month=1, year=2026, school=school,
                defaults=dict(base_salary=Decimal("4500"), gross_salary=Decimal("5000"),
                              total_deductions=Decimal("500"), net_salary=Decimal("4500"),
                              status="paid", payment_date=date(2026, 1, 28)),
            )

        self.stdout.write(self.style.SUCCESS(f"  Payroll: {len(teachers)} payslips"))

        # ── HR ──
        from apps.hr.models import Employee, LeaveType, LeaveRequest

        for i, user in enumerate(teachers + [staff_users.get("accountant"), staff_users.get("librarian")]):
            if user is None:
                continue
            Employee.objects.get_or_create(
                user=user,
                defaults=dict(school=school, employee_id=f"EMP{i+1:04d}",
                              designation="Teacher" if user.role == "teacher" else user.role.title(),
                              date_of_joining=date(2023, 8, 1),
                              department=departments[i % len(departments)],
                              contract_type="permanent"),
            )

        leave_types = []
        for name, days in [("Sick Leave", 12), ("Casual Leave", 10), ("Vacation", 20)]:
            lt, _ = LeaveType.objects.get_or_create(name=name, defaults=dict(school=school, max_days_per_year=days))
            leave_types.append(lt)

        for i, user in enumerate(teachers[:3]):
            LeaveRequest.objects.get_or_create(
                employee=user, leave_type=leave_types[i % len(leave_types)],
                start_date=date(2026, 2, 10 + i),
                defaults=dict(end_date=date(2026, 2, 12 + i), days=2,
                              reason="Personal reasons", status="approved" if i < 2 else "pending",
                              approved_by=staff_users.get("principal") if i < 2 else None),
            )

        self.stdout.write(self.style.SUCCESS(f"  HR: {Employee.objects.count()} employees"))

        # ── Timetable ──
        from apps.timetable.models import Period, Room as TimetableRoom, TimetableEntry

        periods = []
        period_times = [
            ("Period 1", time(8, 0), time(8, 45)), ("Period 2", time(8, 50), time(9, 35)),
            ("Period 3", time(9, 40), time(10, 25)), ("Break", time(10, 25), time(10, 45)),
            ("Period 4", time(10, 45), time(11, 30)), ("Period 5", time(11, 35), time(12, 20)),
            ("Lunch", time(12, 20), time(13, 0)), ("Period 6", time(13, 0), time(13, 45)),
        ]
        for i, (name, start, end) in enumerate(period_times):
            p, _ = Period.objects.get_or_create(
                name=name, school=school,
                defaults=dict(start_time=start, end_time=end, order=i + 1,
                              is_break=name in ("Break", "Lunch")),
            )
            periods.append(p)

        rooms = []
        for name, code in [("Room 101", "R101"), ("Room 102", "R102"), ("Room 201", "R201"),
                           ("Lab 1", "LAB1"), ("Library", "LIB"), ("Sports Hall", "SPRT")]:
            r, _ = TimetableRoom.objects.get_or_create(name=name, code=code, defaults=dict(school=school, capacity=40))
            rooms.append(r)

        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        tt_count = 0
        teaching_periods = [p for p in periods if "Break" not in p.name and "Lunch" not in p.name]
        for cls in classes[:3]:
            for day in days:
                for k, period in enumerate(teaching_periods):
                    subj = subjects[k % len(subjects)]
                    _, created = TimetableEntry.objects.get_or_create(
                        school=school, academic_year=ay, class_obj=cls,
                        period=period, day_of_week=day,
                        defaults=dict(subject=subj, teacher=teachers[k % len(teachers)],
                                      room=rooms[k % len(rooms)]),
                    )
                    if created:
                        tt_count += 1

        self.stdout.write(self.style.SUCCESS(f"  Timetable: {tt_count} entries"))

        # ── Library ──
        from apps.library.models import Book, BookCategory, BookCopy, LibraryMembership

        categories = []
        for name in ["Fiction", "Non-Fiction", "Science", "Mathematics", "History", "Reference"]:
            cat, _ = BookCategory.objects.get_or_create(name=name, defaults=dict(school=school))
            categories.append(cat)

        books_data = [
            ("To Kill a Mockingbird", "978-0061120084", "Harper Lee", 0),
            ("1984", "978-0451524935", "George Orwell", 0),
            ("A Brief History of Time", "978-0553380163", "Stephen Hawking", 2),
            ("The Elements of Style", "978-0205309023", "Strunk & White", 5),
            ("Sapiens", "978-0062316097", "Yuval Noah Harari", 4),
            ("Introduction to Algorithms", "978-0262033848", "Thomas Cormen", 3),
            ("Physics: Principles", "978-0321976444", "Douglas Giancoli", 2),
            ("World History", "978-1305091207", "William Duiker", 4),
        ]
        books = []
        for title, isbn, author, cat_idx in books_data:
            b, _ = Book.objects.get_or_create(
                isbn=isbn, school=school,
                defaults=dict(title=title, author=author, category=categories[cat_idx],
                              publisher="Academic Press", total_copies=5, available_copies=3),
            )
            books.append(b)
            for copy_num in range(1, 4):
                BookCopy.objects.get_or_create(
                    book=b, copy_number=copy_num,
                    defaults=dict(barcode=f"{isbn[-4:]}-{copy_num:02d}", is_available=True, condition="good"),
                )

        # Library memberships for students
        librarian_user = staff_users.get("librarian")
        if librarian_user:
            LibraryMembership.objects.get_or_create(
                user=librarian_user, defaults=dict(school=school, membership_number="LIB-STAFF-001",
                                                    membership_type="staff", max_books=10),
            )
        for i, st in enumerate(students[:15]):
            LibraryMembership.objects.get_or_create(
                user=st.user, defaults=dict(school=school, membership_number=f"LIB-STU-{i+1:03d}",
                                             membership_type="student", max_books=3),
            )

        self.stdout.write(self.style.SUCCESS(f"  Library: {len(books)} books"))

        # ── Transport ──
        from apps.transport.models import Vehicle, Driver, BusRoute, BusStop

        vehicles = []
        for num, vtype, cap in [("SPR-001", "bus", 40), ("SPR-002", "bus", 40), ("SPR-003", "van", 15)]:
            v, _ = Vehicle.objects.get_or_create(
                vehicle_number=num, school=school,
                defaults=dict(vehicle_type=vtype, make="Blue Bird", model="Vision",
                              year=2022, capacity=cap, fuel_type="diesel",
                              insurance_expiry=date(2027, 6, 30),
                              registration_expiry=date(2027, 6, 30)),
            )
            vehicles.append(v)

        driver, _ = Driver.objects.get_or_create(
            license_number="DL-SPR-001", school=school,
            defaults=dict(name="John Baker", phone="+1-555-3001",
                          license_expiry=date(2028, 12, 31)),
        )

        routes = []
        for name, code, start, end, fee in [
            ("North Route", "NR01", "Downtown", "Main Campus", Decimal("150")),
            ("South Route", "SR01", "Southside", "Main Campus", Decimal("180")),
        ]:
            r, _ = BusRoute.objects.get_or_create(
                code=code, school=school,
                defaults=dict(name=name, start_location=start, end_location=end,
                              estimated_time_minutes=35, distance_km=Decimal("12.5"),
                              monthly_fee=fee, vehicle=vehicles[0], driver=driver),
            )
            routes.append(r)
            for j, (sname, ptime, dtime) in enumerate([
                ("Oak Street", time(7, 15), time(15, 30)),
                ("Pine Avenue", time(7, 25), time(15, 20)),
                ("Maple Drive", time(7, 35), time(15, 10)),
            ]):
                BusStop.objects.get_or_create(
                    name=f"{sname} ({code})", route=r,
                    defaults=dict(order=j + 1, pickup_time=ptime, drop_time=dtime),
                )

        self.stdout.write(self.style.SUCCESS(f"  Transport: {len(vehicles)} vehicles, {len(routes)} routes"))

        # ── Hostel ──
        from apps.hostel.models import Building, Floor, Room as HostelRoom

        building, _ = Building.objects.get_or_create(
            code="BLK-A", school=school,
            defaults=dict(name="Block A - Boys", warden=staff_users.get("principal")),
        )
        for floor_num in range(1, 4):
            floor, _ = Floor.objects.get_or_create(
                floor_number=floor_num, building=building,
                defaults=dict(name=f"Floor {floor_num}"),
            )
            for room_num in range(1, 6):
                HostelRoom.objects.get_or_create(
                    room_number=f"{floor_num}{room_num:02d}", floor=floor,
                    defaults=dict(room_type="double" if room_num <= 3 else "single",
                                  capacity=2 if room_num <= 3 else 1,
                                  monthly_fee=Decimal("300") if room_num <= 3 else Decimal("500")),
                )

        self.stdout.write(self.style.SUCCESS(f"  Hostel: 1 building, 3 floors, 15 rooms"))

        # ── Communication ──
        from apps.communication.models import Announcement, Message

        announcements_data = [
            ("Welcome Back to School!", "Welcome to the 2025-2026 academic year. We look forward to a great year!"),
            ("Parent-Teacher Meeting", "The next PTA meeting is scheduled for November 15th at 4:00 PM."),
            ("Science Fair", "Annual science fair will be held on December 1st. All students are encouraged to participate."),
            ("Winter Break Notice", "School will be closed from December 21st to January 5th for winter break."),
            ("Sports Day", "Annual Sports Day is on March 15th. Students should register by March 1st."),
        ]
        principal_user = staff_users.get("principal")
        for title, content in announcements_data:
            Announcement.objects.get_or_create(
                title=title, school=school,
                defaults=dict(content=content, author=principal_user,
                              publish_date=timezone.now(), target_audience="all"),
            )

        # Sample messages
        if principal_user and parents:
            Message.objects.get_or_create(
                subject="Welcome to Springfield Academy", school=school,
                sender=principal_user,
                defaults=dict(body="Dear Parent, welcome to our school community!",
                              recipient=parents[0].user),
            )

        self.stdout.write(self.style.SUCCESS(f"  Communication: {len(announcements_data)} announcements"))

        # ── LMS ──
        from apps.lms.models import Assignment, Course, Module, Lesson

        courses_data = [
            ("Introduction to Algebra", subjects[0], classes[5]),
            ("Basic Physics", subjects[1], classes[6]),
            ("English Composition", subjects[4], classes[4]),
        ]
        for title, subj, cls in courses_data:
            course, _ = Course.objects.get_or_create(
                title=title, school=school,
                defaults=dict(subject=subj, class_obj=cls, instructor=teachers[0],
                              description=f"Comprehensive {title} course", is_published=True),
            )
            m, _ = Module.objects.get_or_create(title=f"{title} - Unit 1", course=course,
                                                 defaults=dict(order=1, description="First unit"))
            Lesson.objects.get_or_create(title=f"Lesson 1: Introduction", module=m,
                                          defaults=dict(order=1, content="Welcome to this lesson.",
                                                        content_type="text"))

        # Assignments
        for i, (cls, subj) in enumerate([(classes[5], subjects[0]), (classes[6], subjects[1])]):
            Assignment.objects.get_or_create(
                title=f"Homework {i+1}: {subj.name}",
                defaults=dict(class_obj=cls, subject=subj, teacher=teachers[0],
                              description=f"Complete exercises 1-10", due_date=date(2026, 2, 28),
                              max_marks=100),
            )

        self.stdout.write(self.style.SUCCESS(f"  LMS: {len(courses_data)} courses, 2 assignments"))

        # ── Inventory ──
        from apps.inventory.models import Asset, AssetCategory

        asset_cats = []
        for name in ["Furniture", "Electronics", "Lab Equipment", "Sports Equipment"]:
            ac, _ = AssetCategory.objects.get_or_create(name=name, defaults=dict(school=school))
            asset_cats.append(ac)

        assets_data = [
            ("Student Desk", "DESK", "good", "in_use", 0, 200),
            ("Projector", "PROJ", "good", "in_use", 1, 6),
            ("Microscope", "MICRO", "good", "available", 2, 10),
            ("Basketball", "BALL", "good", "in_use", 3, 15),
            ("Whiteboard", "WB", "good", "in_use", 1, 20),
            ("Laptop", "LAP", "good", "in_use", 1, 30),
        ]
        for name, code_prefix, condition, status, cat_idx, qty in assets_data:
            for j in range(min(qty, 3)):  # create max 3 per type
                Asset.objects.get_or_create(
                    asset_code=f"{code_prefix}-{j+1:03d}", school=school,
                    defaults=dict(name=f"{name} #{j+1}", category=asset_cats[cat_idx],
                                  condition=condition, status=status,
                                  purchase_date=date(2024, 1, 15),
                                  purchase_price=Decimal("250")),
                )

        self.stdout.write(self.style.SUCCESS(f"  Inventory: {Asset.objects.count()} assets"))

        # ── Health ──
        from apps.health.models import HealthVisit, MedicalRecord

        for st in students[:20]:
            MedicalRecord.objects.get_or_create(
                student=st,
                defaults=dict(blood_group=st.blood_group or "O+",
                              allergies="None known", chronic_conditions="None"),
            )

        health_reasons = ["Headache", "Stomach ache", "Minor injury", "Fever", "Allergic reaction"]
        for i in range(10):
            HealthVisit.objects.get_or_create(
                student=students[i],
                visit_date=date(2026, 1, 10 + i),
                defaults=dict(reason=health_reasons[i % len(health_reasons)],
                              diagnosis="Treated and released",
                              treatment="Rest and medication",
                              attended_by=staff_users.get("nurse")),
            )

        self.stdout.write(self.style.SUCCESS(f"  Health: {MedicalRecord.objects.count()} records"))

        # ── Discipline ──
        from apps.discipline.models import BehaviorCategory, DisciplineIncident

        beh_cats = []
        for name, sev in [("Tardiness", 1), ("Disruption", 2), ("Bullying", 3), ("Academic Dishonesty", 3)]:
            bc, _ = BehaviorCategory.objects.get_or_create(
                name=name, defaults=dict(school=school, severity_level=sev),
            )
            beh_cats.append(bc)

        incidents = [
            (students[10], beh_cats[0], "Late to class three times", "resolved", "warning"),
            (students[15], beh_cats[1], "Disrupting class during lecture", "resolved", "detention"),
            (students[20], beh_cats[0], "Arrived 30 minutes late", "reported", ""),
        ]
        for st, cat, desc, status, action in incidents:
            DisciplineIncident.objects.get_or_create(
                student=st, incident_date=timezone.make_aware(timezone.datetime(2026, 1, 15, 10, 0)),
                defaults=dict(school=school, description=desc, category=cat,
                              status=status, action_taken=action, reported_by=teachers[0]),
            )

        self.stdout.write(self.style.SUCCESS(f"  Discipline: {DisciplineIncident.objects.count()} incidents"))

        # ── Admissions ──
        from apps.admissions.models import AdmissionApplication, AdmissionPeriod

        period, _ = AdmissionPeriod.objects.get_or_create(
            name="2026-2027 Admissions", school=school,
            defaults=dict(academic_year=ay, start_date=date(2026, 3, 1),
                          end_date=date(2026, 7, 31), is_active=True),
        )

        applicants = [
            ("John", "Doe", "john.doe@email.com", classes[0]),
            ("Jane", "Smith", "jane.smith@email.com", classes[0]),
            ("Alex", "Johnson", "alex.j@email.com", classes[2]),
            ("Maria", "Garcia", "maria.g@email.com", classes[4]),
            ("Sam", "Williams", "sam.w@email.com", classes[3]),
        ]
        for first, last, email, cls in applicants:
            AdmissionApplication.objects.get_or_create(
                email=email, admission_period=period,
                defaults=dict(
                    application_number=f"APP-2026-{first[:3].upper()}{last[:3].upper()}",
                    first_name=first, last_name=last, school=school,
                    applying_for_class=cls, date_of_birth=date(2015, 6, 15),
                    gender="male" if first in ("John", "Alex", "Sam") else "female",
                    parent_name=f"Mr. {last}", parent_email=f"parent.{last.lower()}@email.com",
                    parent_phone="+1-555-9999",
                    status="under_review",
                ),
            )

        self.stdout.write(self.style.SUCCESS(f"  Admissions: {AdmissionApplication.objects.count()} applications"))

        # ── Analytics ──
        from apps.analytics.models import DashboardWidget

        widgets = [
            ("Total Students", "stat", "students.Student", 1, "school_admin"),
            ("Attendance Rate", "stat", "attendance.StudentAttendance", 2, "school_admin"),
            ("Revenue", "stat", "finance.Payment", 3, "accountant"),
            ("Pending Fees", "stat", "finance.Invoice", 4, "accountant"),
        ]
        for title, wtype, source, pos, role in widgets:
            DashboardWidget.objects.get_or_create(
                title=title, school=school,
                defaults=dict(widget_type=wtype, data_source=source, position=pos, role=role),
            )

        self.stdout.write(self.style.SUCCESS(f"  Analytics: {len(widgets)} dashboard widgets"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
        self.stdout.write(self.style.WARNING("  Login credentials for all seeded users: password123"))
        self.stdout.write(self.style.WARNING("  Superadmin: admin@school.com / admin123"))
