# 3/5
from datetime import date, time, timedelta
from decimal import Decimal

from apps.route_schedules.models import (
    ASeries,
    ASeriesLink,
    Route,
    RouteStation,
    SSeries,
    TrainStation,
    TripSchedule,
)
from apps.trains.models import Train


def seed_routes_and_schedules(trains: dict[str, Train]) -> dict[str, TripSchedule]:
    """
    Seed routes, stations, links, and trip schedules.
    Returns a clean key -> TripSchedule lookup dictionary for downstream ticket seeding.
    """
    print("SEED[3/5] Seeding routes, stations, links, and trip schedules...")

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

    # 6. ASeriesLinks (11 bidirectional edges; `bidirectional=True` auto-syncs the reverse link via post_save signal)
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

    for origin_name, dest_name, cost, duration in undirected_a_links:
        link, _ = ASeriesLink.objects.update_or_create(
            a_origin=a_stations[origin_name],
            a_destination=a_stations[dest_name],
            defaults={
                "travel_cost": cost,
                "travel_duration": duration,
                "bidirectional": True,
            },
        )
        link.full_clean()

    # 7. TripSchedules (keyed by readable domain keys -> TripSchedule instance)
    schedules_data = [
        # S-Series clockwise loop (Beaver's Dam -> Allies' Enclave -> The Wardrobe -> The Lamp Post -> Beaver's Dam)
        ("s_dam_to_enclave", "451621", "S-Series", "Beaver's Dam", "Allies' Enclave", date(2026, 11, 16), time(8, 0), time(8, 5), Decimal("2.00")),
        ("s_enclave_to_wardrobe", "451621", "S-Series", "Allies' Enclave", "The Wardrobe", date(2026, 11, 16), time(8, 10), time(8, 15), Decimal("2.00")),
        ("s_wardrobe_to_lamppost", "428930", "S-Series", "The Wardrobe", "The Lamp Post", date(2026, 11, 16), time(8, 20), time(8, 25), Decimal("2.00")),
        ("s_lamppost_to_dam", "445382", "S-Series", "The Lamp Post", "Beaver's Dam", date(2026, 11, 16), time(8, 30), time(8, 35), Decimal("2.00")),
        # A-Series inter-town network trips
        ("a_enclave_to_tumms", "402938", "A-Series", "Allies' Enclave", "Mr. Tumms", date(2026, 11, 16), time(9, 0), time(9, 35), Decimal("8.00")),
        ("a_enclave_to_lawn", "429844", "A-Series", "Allies' Enclave", "Dancing Lawn", date(2026, 11, 16), time(10, 0), time(11, 30), Decimal("15.00")),
        ("a_lawn_to_anvard", "429844", "A-Series", "Dancing Lawn", "Anvard", date(2026, 11, 16), time(12, 0), time(13, 10), Decimal("13.50")),
        ("a_enclave_to_aslan", "411827", "A-Series", "Allies' Enclave", "Aslan's Camp", date(2026, 11, 17), time(13, 0), time(14, 45), Decimal("18.00")),
        ("a_cauldron_to_christmas", "409382", "A-Series", "Cauldron Pool", "Father Christmas", date(2026, 11, 17), time(15, 0), time(15, 40), Decimal("9.50")),
        ("a_witch_to_stonetable", "409382", "A-Series", "Witch's Camp", "The Stone Table", date(2026, 11, 17), time(16, 15), time(16, 50), Decimal("8.50")),
    ]

    trip_schedules: dict[str, TripSchedule] = {}
    for key, train_id, route_name, origin_name, dest_name, trip_date, dep_time, arr_time, cost in schedules_data:
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
        trip_schedules[key] = schedule

    print(
        f"      OK - {Route.objects.count()} Routes, "
        f"{TrainStation.objects.count()} Stations, "
        f"{RouteStation.objects.count()} RouteStations, "
        f"{SSeries.objects.count()} SSeries, "
        f"{ASeries.objects.count()} ASeries, "
        f"{ASeriesLink.objects.count()} ASeriesLinks, "
        f"{TripSchedule.objects.count()} TripSchedules."
    )
    return trip_schedules
