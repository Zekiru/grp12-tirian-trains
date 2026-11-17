"""Optional Reset Step: Clear existing database records in reverse FK dependency order."""

from apps.route_schedules.models import (
    ASeries,
    ASeriesLink,
    Route,
    RouteStation,
    SSeries,
    TrainStation,
    TripSchedule,
)
from apps.trains.models import Maintenance, MaintenanceCrew, Train


def reset_data() -> None:
    """Delete data in reverse foreign-key dependency order."""
    print("[Reset] Clearing existing records...")
    TripSchedule.objects.all().delete()
    ASeriesLink.objects.all().delete()
    ASeries.objects.all().delete()
    SSeries.objects.all().delete()
    RouteStation.objects.all().delete()
    TrainStation.objects.all().delete()
    Route.objects.all().delete()
    Maintenance.objects.all().delete()
    MaintenanceCrew.objects.all().delete()
    Train.objects.all().delete()
    print("        OK - Tables cleared.")
