from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand, CommandError

from app.scheduled_job.address_job import (
    update_cities_async,
    update_streets_async,
)


class Command(BaseCommand):
    help = "Update SCAT cities and streets"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cities-only",
            action="store_true",
            help="Update only cities from SCAT.",
        )
        parser.add_argument(
            "--streets-only",
            action="store_true",
            help="Update only streets from SCAT.",
        )

    def handle(self, *args, **options):
        cities_only = options["cities_only"]
        streets_only = options["streets_only"]

        if cities_only and streets_only:
            raise CommandError(
                "Use either --cities-only or --streets-only, not both.",
            )

        should_update_cities = not streets_only
        should_update_streets = not cities_only

        if should_update_cities:
            self.stdout.write("Updating SCAT cities...")
            cities_count = async_to_sync(update_cities_async)()
            self.stdout.write(
                self.style.SUCCESS(f"Updated {cities_count} cities."),
            )

        if should_update_streets:
            self.stdout.write("Updating SCAT streets...")
            streets_count = async_to_sync(update_streets_async)()
            self.stdout.write(
                self.style.SUCCESS(f"Updated {streets_count} streets."),
            )
