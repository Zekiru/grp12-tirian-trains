"""Step 2: Remove system-generated migration files across app directories."""

import shutil
from rebuilding.env_loader import BASE_DIR


def delete_app_migrations() -> None:
    """Delete all generated migration files (keeping __init__.py) in apps/ and app/ folders."""
    print("REBUILD[2/4] Deleting system-generated migrations in app directories...")
    deleted_count = 0

    for folder_name in ("apps", "app"):
        apps_dir = BASE_DIR / folder_name
        if not apps_dir.is_dir():
            continue

        for migrations_dir in apps_dir.glob("*/migrations"):
            if not migrations_dir.is_dir():
                continue

            for item in migrations_dir.iterdir():
                if item.name == "__init__.py":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                    if item.suffix == ".py":
                        deleted_count += 1

    print(f"      OK - Removed {deleted_count} migration file(s).")
