"""
Database Seeding Entry Point.
Place `seed.py` and the `seeding/` folder in the base folder of the Django project.

Usage:
    python seed.py          # Idempotent seed (safe to re-run)
    python seed.py --reset  # Clears seeded tables first, then re-seeds
"""

import argparse
from django.db import transaction

from seeding.django_env import setup_django

setup_django()

from apps.tickets.models import Customer, Ticket, TicketItinerary
from seeding.checks import run_migration_and_constraint_checks
from seeding.migrations_check import verify_migrations
from seeding.reset import reset_database
from seeding.seed_routes import seed_routes_and_schedules
from seeding.seed_tickets import seed_tickets
from seeding.seed_trains import seed_trains_and_maintenance


def main(reset: bool = False) -> None:
    verify_migrations()

    with transaction.atomic():
        if reset:
            reset_database()

        trains = seed_trains_and_maintenance()
        trip_schedules = seed_routes_and_schedules(trains)
        seed_tickets(trip_schedules)
        run_migration_and_constraint_checks()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Tirian Trains database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing records before seeding.",
    )
    args = parser.parse_args()
    main(reset=args.reset)
