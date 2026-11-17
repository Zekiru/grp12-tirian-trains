"""Step 4: Post-seed model property, signal, duration calculation, and DB CheckConstraint checks."""

from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.db import IntegrityError, transaction

from apps.route_schedules.models import ASeries, ASeriesLink, TrainStation, TripSchedule


def run_migration_and_constraint_checks() -> None:
    """Verify model properties, auto-sync signals, trip_duration calculation, and DB CheckConstraints."""
    print("[4/4] Running migration & database constraint sanity checks...")

    # 1. Django system check
    call_command("check")

    # 2. Verify TrainStation.is_s_series and TrainStation.is_a_series properties
    enclave = TrainStation.objects.get(station_name="Allies' Enclave")
    wardrobe = TrainStation.objects.get(station_name="The Wardrobe")
    anvard = TrainStation.objects.get(station_name="Anvard")
    assert enclave.is_s_series and enclave.is_a_series, "Allies' Enclave must belong to both S-Series and A-Series."
    assert wardrobe.is_s_series and not wardrobe.is_a_series, "The Wardrobe must belong only to S-Series."
    assert anvard.is_a_series and not anvard.is_s_series, "Anvard must belong only to A-Series."

    # 3. Verify bidirectional ASeriesLink signal created reverse edges (22 directed links total)
    assert ASeriesLink.objects.count() == 22, (
        f"Expected 22 directed ASeriesLinks (11 bidirectional pairs), got {ASeriesLink.objects.count()}."
    )

    # 4. Verify TripSchedule.trip_duration was computed accurately in save()
    sample_trip = TripSchedule.objects.filter(route_id="S-Series").first()
    if sample_trip is None or sample_trip.trip_duration != timedelta(minutes=5):
        raise AssertionError(
            f"Expected S-Series trip_duration of 5 minutes, got {getattr(sample_trip, 'trip_duration', None)}."
        )

    # 5. Verify DB CheckConstraint enforcement via atomic savepoint rollback
    station_a = ASeries.objects.first()
    try:
        with transaction.atomic():
            ASeriesLink.objects.create(
                a_origin=station_a,
                a_destination=station_a,
                travel_cost=Decimal("10.00"),
                travel_duration=timedelta(minutes=30),
            )
            raise AssertionError(
                "Expected IntegrityError for self-referencing ASeriesLink (`invalid_link` constraint), but insert succeeded."
            )
    except IntegrityError:
        pass

    print("      OK - System checks, series properties, bidirectional links, trip_duration, and CheckConstraints verified.")
