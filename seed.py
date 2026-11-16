"""
Database seed script & migration integrity checker.
Place this file in the base folder of the Django project (next to manage.py).

Usage:
    python seed.py          # Seed/update records idempotently & run model/constraint checks
    python seed.py --reset  # Clear existing records before re-seeding
"""

import os
import re
import sys
from datetime import date, time, timedelta
from decimal import Decimal
from pathlib import Path


def setup_django() -> None:
    """Detect DJANGO_SETTINGS_MODULE from manage.py and initialize Django."""
    base_dir = Path(__file__).resolve().parent
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
    django.setup()


setup_django()

from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor

from apps.trains.models import Maintenance, MaintenanceCrew, Train
from apps.route_schedules.models import (
    ASeries,
    ASeriesLink,
    Route,
    RouteStation,
    SSeries,
    TrainStation,
    TripSchedule,
)


def verify_migrations() -> None:
    """Ensure all migrations have been applied before seeding."""
    print("[1/4] Checking database connection and pending migrations...")
    connection.ensure_connection()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    plan = executor.migration_plan(targets)
    if plan:
        pending = [f"{migration.app_label}.{migration.name}" for migration, _ in plan]
        raise RuntimeError(
            f"Unapplied migrations detected: {', '.join(pending)}. "
            "Run `python manage.py migrate` first."
        )
    print("      OK - All migrations are up to date.")


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


def seed_trains_and_maintenance() -> dict[str, Train]:
    """Seed Train, MaintenanceCrew, and Maintenance records."""
    print("[2/4] Seeding trains and maintenance logs...")

    trains_data = [
        {
            "train_id": "TRN001",
            "model_series": "S",
            "model_number": "101",
            "max_speed": 120,
            "seat_count": 70,
            "toilet_count": 4,
            "reclining_seats": True,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": False,
            "vending_machines": True,
            "food_service": False,
        },
        {
            "train_id": "TRN002",
            "model_series": "S",
            "model_number": "102",
            "max_speed": 110,
            "seat_count": 60,
            "toilet_count": 3,
            "reclining_seats": False,
            "folding_tables": False,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": False,
        },
        {
            "train_id": "TRN003",
            "model_series": "A",
            "model_number": "201",
            "max_speed": 160,
            "seat_count": 80,
            "toilet_count": 5,
            "reclining_seats": True,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": True,
        },
        {
            "train_id": "TRN004",
            "model_series": "A",
            "model_number": "202",
            "max_speed": 150,
            "seat_count": 75,
            "toilet_count": 4,
            "reclining_seats": False,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": True,
            "food_service": True,
        },
    ]

    trains: dict[str, Train] = {}
    for item in trains_data:
        train, _ = Train.objects.update_or_create(
            train_id=item["train_id"],
            defaults=item,
        )
        train.full_clean()
        trains[train.train_id] = train

    crew_data = [
        ("Benicci", "Ramoh"),
        ("Nami", "Khitsu"),
        ("Clint", "Itson"),
        ("Kanna", "Wand"),
    ]

    crew_members: dict[str, MaintenanceCrew] = {}
    for firstname, lastname in crew_data:
        crew, _ = MaintenanceCrew.objects.get_or_create(
            crew_firstname=firstname,
            crew_lastname=lastname,
        )
        crew.full_clean()
        crew_members[lastname] = crew

    maintenance_data = [
        ("TRN001", "Ramoh", 0, date(2026, 10, 1), "Full interior cleaning", "Routine sanitation and seat inspection."),
        ("TRN001", "Khitsu", 1, date(2026, 10, 15), "Brake disc replacement", "Replaced front bogie brake pads and discs."),
        ("TRN002", "Itson", 2, date(2026, 10, 10), "Engine oil change", "Standard lubrication and filter swap."),
        ("TRN003", "Wand", 0, date(2026, 10, 20), "Electrical diagnostics", "Tested cabin lighting, doors, and HVAC."),
        ("TRN004", "Khitsu", 1, date(2026, 11, 2), "Suspension calibration", "Adjusted air suspension pressure."),
    ]

    for train_id, crew_lastname, condition, maint_date, task, description in maintenance_data:
        log, _ = Maintenance.objects.update_or_create(
            train=trains[train_id],
            crew=crew_members[crew_lastname],
            maintenance_date=maint_date,
            task=task,
            defaults={
                "condition": condition,
                "description": description,
            },
        )
        log.full_clean()

    print(
        f"      OK - {Train.objects.count()} Trains, "
        f"{MaintenanceCrew.objects.count()} Crew, "
        f"{Maintenance.objects.count()} Maintenance logs."
    )
    return trains


def seed_routes_and_schedules(trains: dict[str, Train]) -> None:
    """Seed Route ('S-Series' and 'A-Series'), TrainStation, RouteStation, SSeries, ASeries, ASeriesLink, and TripSchedule."""
    print("[3/4] Seeding routes, stations, links, and trip schedules...")

    # 1. Routes (strictly 'S-Series' for Western Woods loop, 'A-Series' for inter-town network)
    routes_data = [
        ("S-Series", Decimal("2.00"), timedelta(minutes=5)),
        ("A-Series", None, None),
    ]
    routes: dict[str, Route] = {}
    for route_name, fixed_cost, fixed_duration in routes_data:
        route, _ = Route.objects.update_or_create(
            route_name=route_name,
            defaults={
                "fixed_cost": fixed_cost,
                "fixed_travel_duration": fixed_duration,
            },
        )
        route.full_clean()
        routes[route_name] = route

    # 2. TrainStations (4 Western Woods S-Series loop stations + 9 other inter-town A-Series stations = 13 total)
    s_station_names = [
        "Beaver's Dam",
        "Allies' Enclave",
        "The Wardrobe",
        "The Lamp Post",
    ]
    a_station_names = [
        "Mr. Tumms",
        "Allies' Enclave",
        "Aslan's Camp",
        "Cauldron Pool",
        "Witch's Camp",
        "The Stone Table",
        "Father Christmas",
        "Dancing Lawn",
        "Cherry Tree",
        "Anvard",
    ]

    all_station_names = list(dict.fromkeys(s_station_names + a_station_names))
    stations: dict[str, TrainStation] = {}
    for name in all_station_names:
        station, _ = TrainStation.objects.get_or_create(station_name=name)
        station.full_clean()
        stations[name] = station

    # 3. RouteStations (post_save signal automatically creates ASeries records for 'A-Series' members)
    for station_name in s_station_names:
        rs, _ = RouteStation.objects.get_or_create(
            route=routes["S-Series"],
            station=stations[station_name],
        )
        rs.full_clean()

    for station_name in a_station_names:
        rs, _ = RouteStation.objects.get_or_create(
            route=routes["A-Series"],
            station=stations[station_name],
        )
        rs.full_clean()

    # 4. SSeries (clockwise loop order: Beaver's Dam -> Allies' Enclave -> The Wardrobe -> The Lamp Post)
    for order, station_name in enumerate(s_station_names, start=1):
        s_obj, _ = SSeries.objects.update_or_create(
            s_station=stations[station_name],
            defaults={"route_order": order},
        )
        s_obj.full_clean()

    # 5. Fetch ASeries records (auto-synced by RouteStation signal, with fallback get_or_create)
    a_stations: dict[str, ASeries] = {}
    for station_name in a_station_names:
        a_obj, _ = ASeries.objects.get_or_create(a_station=stations[station_name])
        a_obj.full_clean()
        a_stations[station_name] = a_obj

    # 6. ASeriesLinks (11 bidirectional inter-town edges = 22 directed links from the routing diagram)
    undirected_a_links = [
        ("Mr. Tumms", "Allies' Enclave", Decimal("8.00"), timedelta(minutes=35)),
        ("Allies' Enclave", "Aslan's Camp", Decimal("18.00"), timedelta(hours=1, minutes=45)),
        ("Allies' Enclave", "Cauldron Pool", Decimal("10.00"), timedelta(minutes=45)),
        ("Allies' Enclave", "Dancing Lawn", Decimal("15.00"), timedelta(hours=1, minutes=30)),
        ("Cauldron Pool", "Father Christmas", Decimal("9.50"), timedelta(minutes=40)),
        ("Cauldron Pool", "Cherry Tree", Decimal("14.00"), timedelta(hours=1, minutes=15)),
        ("Father Christmas", "Cherry Tree", Decimal("7.50"), timedelta(minutes=30)),
        ("Father Christmas", "Witch's Camp", Decimal("16.00"), timedelta(hours=1, minutes=20)),
        ("Witch's Camp", "The Stone Table", Decimal("8.50"), timedelta(minutes=35)),
        ("The Stone Table", "Dancing Lawn", Decimal("11.00"), timedelta(minutes=50)),
        ("Dancing Lawn", "Anvard", Decimal("13.50"), timedelta(hours=1, minutes=10)),
    ]

    for station_u, station_v, cost, duration in undirected_a_links:
        for origin_name, dest_name in ((station_u, station_v), (station_v, station_u)):
            link, _ = ASeriesLink.objects.update_or_create(
                a_origin=a_stations[origin_name],
                a_destination=a_stations[dest_name],
                defaults={
                    "travel_cost": cost,
                    "travel_duration": duration,
                },
            )
            link.full_clean()

    # 7. TripSchedules (S-Series clockwise loop trips = 5 min & 2.00; A-Series trips match ASeriesLink cost & duration)
    schedules_data = [
        # S-Series clockwise loop (Beaver's Dam -> Allies' Enclave -> The Wardrobe -> The Lamp Post -> Beaver's Dam)
        ("TRN001", "S-Series", "Beaver's Dam", "Allies' Enclave", date(2026, 11, 16), time(8, 0), time(8, 5), Decimal("2.00")),
        ("TRN001", "S-Series", "Allies' Enclave", "The Wardrobe", date(2026, 11, 16), time(8, 10), time(8, 15), Decimal("2.00")),
        ("TRN002", "S-Series", "The Wardrobe", "The Lamp Post", date(2026, 11, 16), time(8, 20), time(8, 25), Decimal("2.00")),
        ("TRN002", "S-Series", "The Lamp Post", "Beaver's Dam", date(2026, 11, 16), time(8, 30), time(8, 35), Decimal("2.00")),
        # A-Series inter-town network trips
        ("TRN003", "A-Series", "Allies' Enclave", "Mr. Tumms", date(2026, 11, 16), time(9, 0), time(9, 35), Decimal("8.00")),
        ("TRN003", "A-Series", "Allies' Enclave", "Dancing Lawn", date(2026, 11, 16), time(10, 0), time(11, 30), Decimal("15.00")),
        ("TRN003", "A-Series", "Dancing Lawn", "Anvard", date(2026, 11, 16), time(12, 0), time(13, 10), Decimal("13.50")),
        ("TRN004", "A-Series", "Allies' Enclave", "Aslan's Camp", date(2026, 11, 17), time(13, 0), time(14, 45), Decimal("18.00")),
        ("TRN004", "A-Series", "Cauldron Pool", "Father Christmas", date(2026, 11, 17), time(15, 0), time(15, 40), Decimal("9.50")),
        ("TRN004", "A-Series", "Witch's Camp", "The Stone Table", date(2026, 11, 17), time(16, 15), time(16, 50), Decimal("8.50")),
    ]

    for train_id, route_name, origin_name, dest_name, trip_date, dep_time, arr_time, cost in schedules_data:
        schedule, _ = TripSchedule.objects.update_or_create(
            train=trains[train_id],
            route=routes[route_name],
            origin_station=stations[origin_name],
            destination_station=stations[dest_name],
            trip_date=trip_date,
            departure_time=dep_time,
            defaults={
                "arrival_time": arr_time,
                "trip_cost": cost,
            },
        )
        schedule.full_clean()

    print(
        f"      OK - {Route.objects.count()} Routes, "
        f"{TrainStation.objects.count()} Stations, "
        f"{RouteStation.objects.count()} RouteStations, "
        f"{SSeries.objects.count()} SSeries, "
        f"{ASeries.objects.count()} ASeries, "
        f"{ASeriesLink.objects.count()} ASeriesLinks, "
        f"{TripSchedule.objects.count()} TripSchedules."
    )


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

    # 3. Verify TripSchedule.trip_duration was computed accurately in save()
    sample_trip = TripSchedule.objects.filter(route_id="S-Series").first()
    if sample_trip is None or sample_trip.trip_duration != timedelta(minutes=5):
        raise AssertionError(f"Expected S-Series trip_duration of 5 minutes, got {getattr(sample_trip, 'trip_duration', None)}.")

    # 4. Verify DB CheckConstraint enforcement via atomic savepoint rollback
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

    print("      OK - System checks, series properties, trip_duration, and CheckConstraints verified.")


def main() -> None:
    reset = "--reset" in sys.argv
    verify_migrations()

    with transaction.atomic():
        if reset:
            reset_data()
        trains = seed_trains_and_maintenance()
        seed_routes_and_schedules(trains)

    run_migration_and_constraint_checks()
    print("\nDatabase seeding and migration checks completed successfully!")


if __name__ == "__main__":
    main()
