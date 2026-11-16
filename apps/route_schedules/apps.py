import sys
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def run_seed_after_migrate(sender, **kwargs):
    # Avoid seeding during automated test runs
    if "test" in sys.argv:
        return

    # Importing `seed` here ensures the app registry is ready and all
    # migrations for both `trains` and `route_schedules` are complete.
    import seed
    seed.main()


class RouteScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.route_schedules'

    def ready(self):
        post_migrate.connect(run_seed_after_migrate, sender=self)
