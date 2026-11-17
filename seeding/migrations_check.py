"""Step 1: Database connection & migration state verification."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor


def verify_migrations() -> None:
    """Ensure all migrations have been applied before seeding."""
    print("SEED[1/4] Checking database connection and pending migrations...")
    connection.ensure_connection()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    plan = executor.migration_plan(targets)
    if plan:
        pending = [f"{migration.app_label}.{migration.name}" for migration, _ in plan]
        raise RuntimeError(
            f"Unapplied migrations detected: {', '.join(pending)}. "
            "Run `python manage.py migrate` first."
        )
    print("      OK - All migrations are up to date.")
