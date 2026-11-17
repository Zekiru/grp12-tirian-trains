"""Step 3: Regenerate migrations and apply them (triggering post_migrate seeding)."""

from django.core.management import call_command


def rebuild_migrations_and_database() -> None:
    """Run makemigrations and migrate (which also triggers post_migrate seeding)."""
    print("REBUILD[3/4] Running makemigrations and migrate...")
    call_command("makemigrations")
    call_command("migrate")
