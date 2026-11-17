"""Database reset helper for seeding."""

from apps.route_schedules.models import (
    ASeries,
    ASeriesLink,
    Route,
    RouteStation,
    SSeries,
    TrainStation,
    TripSchedule,
)
from apps.tickets.models import Customer, Ticket, TicketItinerary
from apps.trains.models import Maintenance, MaintenanceCrew, Train


def reset_database() -> None:
    """Clear existing seeded records in reverse foreign-key dependency order."""
    print("[RESET] Clearing existing records...")
    TicketItinerary.objects.all().delete()
    Ticket.objects.all().delete()
    Customer.objects.all().delete()

    TripSchedule.objects.all().delete()
    ASeriesLink.objects.all().delete()
    ASeries.objects.all().delete()
    SSeries.objects.all().delete()
    RouteStation.objects.all().delete()
    Route.objects.all().delete()
    TrainStation.objects.all().delete()

    Maintenance.objects.all().delete()
    Train.objects.all().delete()
    MaintenanceCrew.objects.all().delete()
    print("      OK - Existing data cleared.")
