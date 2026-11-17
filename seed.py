"""
Database seed script & migration integrity checker entry point.
Place `seed.py` and the `seeding/` folder in the base folder of the Django project (next to manage.py).

Usage:
    python seed.py          # Seed/update records idempotently & run model/constraint checks
    python seed.py --reset  # Clear existing records before re-seeding
"""

import sys
from seeding.django_env import setup_django

setup_django()

from django.db import transaction
from seeding.checks import run_migration_and_constraint_checks
from seeding.migrations_check import verify_migrations
from seeding.reset import reset_data
from seeding.seed_routes import seed_routes_and_schedules
from seeding.seed_trains import seed_trains_and_maintenance


def main() -> None:
    reset = "--reset" in sys.argv
    verify_migrations()

    with transaction.atomic():
        if reset:
            reset_data()
        trains = seed_trains_and_maintenance()
        seed_routes_and_schedules(trains)

    run_migration_and_constraint_checks()
    print("\nDatabase seeding and migration checks completed successfully!")


if __name__ == "__main__":
    main()
