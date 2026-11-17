"""Environment loader and Django bootstrapper for reset scripts."""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path | None = None) -> None:
    """Parse a root .env file into os.environ (handles UTF-8, UTF-8-SIG, and PowerShell UTF-16)."""
    target = env_path or (BASE_DIR / ".env")
    if not target.exists():
        print(f"[Env] Warning: {target} not found. Relying on existing environment variables.")
        return

    raw_bytes = target.read_bytes()
    if raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        content = raw_bytes.decode("utf-16")
    else:
        content = raw_bytes.decode("utf-8-sig")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def setup_django() -> None:
    """Detect DJANGO_SETTINGS_MODULE from manage.py and initialize Django if not already loaded."""
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        manage_py = BASE_DIR / "manage.py"
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
            "Set DJANGO_SETTINGS_MODULE in .env or environment variables."
        )

    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()
