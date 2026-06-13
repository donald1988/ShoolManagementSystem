from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsSchoolAdmin, IsTeacher
from apps.students.models import Student

from .models import AttendanceAlert, PeriodAttendance, StudentAttendance, TeacherAttendance
from .serializers import (
    AttendanceAlertSerializer,
    AttendanceReportSerializer,
    BulkAttendanceSerializer,
    PeriodAttendanceSerializer,
    StudentAttendanceSerializer,
    TeacherAttendanceSerializer,
)


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAttendanceSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "class_obj", "section", "date", "status", "academic_year"]
    ordering_fields = ["date"]

    def get_queryset(self):
        qs = StudentAttendance.objects.select_related("student__user", "class_obj", "section")
        user = self.request.user
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__parent_links__parent__user=user)
        elif user.role != "super_admin" and user.school_id:
            qs = qs.filter(student__school_id=user.school_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

    @action(detail=False, methods=["post"])
    def bulk_mark(self, request):
        """Mark attendance for an entire class at once."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        records = []
        for record in data["records"]:
            att, created = StudentAttendance.objects.update_or_create(
                student_id=record["student_id"],
                date=data["date"],
                defaults={
                    "class_obj_id": data["class_id"],
                    "section_id": data.get("section_id"),
                    "academic_year_id": data["academic_year_id"],
                    "status": record.get("status", "present"),
                    "remarks": record.get("remarks", ""),
                    "marked_by": request.user,
                },
            )
            records.append(att)

        return Response(
            {"detail": f"Attendance marked for {len(records)} students."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def report(self, request):
        """Get attendance report for a class."""
        class_id = request.query_params.get("class_id")
        academic_year_id = request.query_params.get("academic_year_id")
        if not class_id or not academic_year_id:
            return Response(
                {"detail": "class_id and academic_year_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        students = Student.objects.filter(current_class_id=class_id)
        report_data = []
        for student in students:
            records = StudentAttendance.objects.filter(
                student=student, academic_year_id=academic_year_id
            )
            total = records.count()
            if total == 0:
                continue
            counts = records.aggregate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
                late=Count("id", filter=Q(status="late")),
                excused=Count("id", filter=Q(status="excused")),
            )
            report_data.append({
                "student_id": student.student_id,
                "student_name": student.user.full_name,
                "total_days": total,
                "present": counts["present"],
                "absent": counts["absent"],
                "late": counts["late"],
                "excused": counts["excused"],
                "percentage": round((counts["present"] + counts["late"]) / total * 100, 2),
            })

        serializer = AttendanceReportSerializer(report_data, many=True)
        return Response(serializer.data)


class PeriodAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodAttendanceSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "class_subject", "date", "period_number", "status"]

    def get_queryset(self):
        return PeriodAttendance.objects.select_related("student__user", "class_subject__subject")

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)


class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherAttendanceSerializer
    permission_classes = [IsSchoolAdmin]
    filterset_fields = ["teacher", "date", "status"]

    def get_queryset(self):
        qs = TeacherAttendance.objects.select_related("teacher__user")
        if self.request.user.role == "teacher":
            qs = qs.filter(teacher__user=self.request.user)
        return qs


class AttendanceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceAlertSerializer
    permission_classes = [IsTeacher]
    filterset_fields = ["student", "alert_type", "is_resolved"]

    def get_queryset(self):
        return AttendanceAlert.objects.select_related("student__user")
