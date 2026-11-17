"""Step 1: Remove the SQLite database file."""

from pathlib import Path
from django.conf import settings
from rebuilding.env_loader import BASE_DIR


def delete_sqlite_database() -> None:
    """Delete the SQLite database file configured in Django settings (or db.sqlite3 fallback)."""
    print("REBUILD[1/4] Deleting SQLite database file...")
    db_path: Path | None = None

    default_db = settings.DATABASES.get("default", {})
    engine = default_db.get("ENGINE", "")
    name = default_db.get("NAME")

    if "sqlite3" in engine and name and str(name) != ":memory:":
        candidate = Path(name)
        db_path = candidate if candidate.is_absolute() else BASE_DIR / candidate
    else:
        fallback = BASE_DIR / "db.sqlite3"
        if fallback.exists():
            db_path = fallback

    if db_path and db_path.exists():
        db_path.unlink()
        print(f"      OK - Deleted {db_path.name}")
    else:
        print("      OK - No SQLite database file found to delete.")
