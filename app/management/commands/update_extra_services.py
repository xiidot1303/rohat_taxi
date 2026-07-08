from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand, CommandError

from app.scheduled_job.extra_services_job import update_extra_services


class Command(BaseCommand):
    help = "Update SCAT extra services"

    def handle(self, *args, **options):
        self.stdout.write("Updating SCAT extra services...")
        extra_services_count = update_extra_services()
        self.stdout.write(
            self.style.SUCCESS(f"Updated {extra_services_count} extra services."),
        )
