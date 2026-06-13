from django.contrib import admin
from .models import Class, ClassSubject, Department, Enrollment, Section, Subject, SubjectPrerequisite, Teacher


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "head", "is_active")
    list_filter = ("school", "is_active")


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school", "numeric_level", "capacity", "is_active")
    list_filter = ("school", "is_active")
    ordering = ("numeric_level",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "class_obj", "capacity", "class_teacher", "is_active")
    list_filter = ("class_obj", "is_active")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "subject_type", "credits", "department", "is_active")
    list_filter = ("subject_type", "is_active", "department")
    search_fields = ("name", "code")


@admin.register(SubjectPrerequisite)
class SubjectPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ("subject", "prerequisite")


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "subject", "teacher", "academic_year", "periods_per_week")
    list_filter = ("academic_year", "class_obj")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "designation", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("employee_id", "user__first_name", "user__last_name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "class_obj", "section", "academic_year", "is_active")
    list_filter = ("academic_year", "class_obj", "is_active")
