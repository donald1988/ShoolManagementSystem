from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = "School Management System"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "Administration"

api_v1_patterns = [
    path("core/", include("apps.core.urls")),
    path("auth/", include("apps.accounts.urls")),
    path("students/", include("apps.students.urls")),
    path("admissions/", include("apps.admissions.urls")),
    path("academics/", include("apps.academics.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("examinations/", include("apps.examinations.urls")),
    path("lms/", include("apps.lms.urls")),
    path("finance/", include("apps.finance.urls")),
    path("payroll/", include("apps.payroll.urls")),
    path("hr/", include("apps.hr.urls")),
    path("communication/", include("apps.communication.urls")),
    path("timetable/", include("apps.timetable.urls")),
    path("library/", include("apps.library.urls")),
    path("transport/", include("apps.transport.urls")),
    path("hostel/", include("apps.hostel.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("health/", include("apps.health.urls")),
    path("discipline/", include("apps.discipline.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("audit/", include("apps.audit.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
