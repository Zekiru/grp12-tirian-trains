"""Django environment bootstrapper for standalone or post-migrate execution."""

import os
import re
import sys
from pathlib import Path


def setup_django() -> None:
    """Detect DJANGO_SETTINGS_MODULE from manage.py and initialize Django if not already loaded."""
    base_dir = Path(__file__).resolve().parent.parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        manage_py = base_dir / "manage.py"
        if manage_py.exists():
            content = manage_py.read_text(encoding="utf-8")
            match = re.search(
                r"""['"]DJANGO_SETTINGS_MODULE['"]\s*,\s*['"]([^'"]+)['"]""",
                content,
            )
            if match:
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", match.group(1))

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        raise RuntimeError(
            "Could not auto-detect DJANGO_SETTINGS_MODULE from manage.py. "
            "Set DJANGO_SETTINGS_MODULE before running seed.py."
        )

    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()
