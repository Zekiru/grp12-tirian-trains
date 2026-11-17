"""Step 4: Create a Django superuser using credentials from .env."""

import os
from django.contrib.auth import get_user_model


def create_superuser_from_env() -> None:
    """Create a Django superuser using credentials from .env."""
    print("[4/4] Creating superuser from .env...")
    username = (
        os.environ.get("DJANGO_SUPERUSER_USERNAME")
        or os.environ.get("SUPERUSER_USERNAME")
        or os.environ.get("ADMIN_USERNAME")
    )
    email = (
        os.environ.get("DJANGO_SUPERUSER_EMAIL")
        or os.environ.get("SUPERUSER_EMAIL")
        or os.environ.get("ADMIN_EMAIL")
        or ""
    )
    password = (
        os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        or os.environ.get("SUPERUSER_PASSWORD")
        or os.environ.get("ADMIN_PASSWORD")
    )

    if not username or not password:
        raise RuntimeError(
            "Missing superuser credentials in .env. Define "
            "DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD "
            "(and optionally DJANGO_SUPERUSER_EMAIL)."
        )

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        print(f"      OK - Superuser '{username}' already exists.")
        return

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"      OK - Superuser '{username}' created.")
