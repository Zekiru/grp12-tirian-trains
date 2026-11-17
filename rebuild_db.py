"""
Development Database & Migration Reset Entry Point.
Place `rebuild_db.py` and the `rebuilding/` folder in the base folder of the Django project (next to manage.py).

Usage:
    python reset_db.py
"""

from rebuilding.env_loader import load_env_file, setup_django

load_env_file()
setup_django()

from rebuilding.clean_db import delete_sqlite_database
from rebuilding.clean_migrations import delete_app_migrations
from rebuilding.rebuild import rebuild_migrations_and_database
from rebuilding.superuser import create_superuser_from_env


def main() -> None:
    delete_sqlite_database()
    delete_app_migrations()
    rebuild_migrations_and_database()
    create_superuser_from_env()
    print("\nDatabase reset, migrations, seeding, and superuser setup completed!")


if __name__ == "__main__":
    main()
