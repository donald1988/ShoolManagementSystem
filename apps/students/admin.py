from django.contrib import admin
from .models import EmergencyContact, Parent, Student, StudentDocument, StudentParent, StudentPromotion


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "current_class", "current_section", "status")
    list_filter = ("status", "gender", "current_class", "school")
    search_fields = ("student_id", "user__first_name", "user__last_name", "user__email")
    raw_id_fields = ("user", "school", "current_class", "current_section")


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("user", "occupation", "school")
    search_fields = ("user__first_name", "user__last_name")
    raw_id_fields = ("user",)


@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = ("student", "parent", "relationship", "is_primary_contact")
    list_filter = ("relationship",)


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "relationship", "phone")


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "document_type", "is_verified")
    list_filter = ("document_type", "is_verified")


@admin.register(StudentPromotion)
class StudentPromotionAdmin(admin.ModelAdmin):
    list_display = ("student", "from_class", "to_class", "academic_year")
    list_filter = ("academic_year",)
