from django.apps import AppConfig


class RoutecheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.route_schedules'

    def ready(self):
        import apps.route_schedules.signals
