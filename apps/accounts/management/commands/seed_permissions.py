from django.core.management.base import BaseCommand

from apps.accounts.models import Permission


class Command(BaseCommand):
    help = "Seed initial permission data for the RBAC system"

    MODULES = [
        "students", "admissions", "academics", "attendance", "examinations",
        "lms", "finance", "payroll", "hr", "communication", "timetable",
        "library", "transport", "hostel", "inventory", "health",
        "discipline", "analytics", "settings",
    ]

    ACTIONS = ["create", "read", "update", "delete", "export", "import", "approve"]

    def handle(self, *args, **options):
        created_count = 0
        for module in self.MODULES:
            for action in self.ACTIONS:
                codename = f"{module}_{action}"
                name = f"Can {action} {module}"
                _, created = Permission.objects.get_or_create(
                    codename=codename,
                    defaults={"name": name, "module": module, "action": action},
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} permissions"))
