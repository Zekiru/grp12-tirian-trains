# 2/5
from datetime import date

from apps.trains.models import Maintenance, MaintenanceCrew, Train


def seed_trains_and_maintenance() -> dict[str, Train]:
    """Seed Train, MaintenanceCrew, and Maintenance records."""
    print("SEED[2/5] Seeding trains and maintenance logs...")

    trains_data = [
        {
            "train_id": "451621",
            "model_series": "S",
            "model_number": "393",
            "max_speed": 120,
            "seat_count": 70,
            "toilet_count": 7,
            "reclining_seats": True,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": False,
            "vending_machines": True,
            "food_service": False,
        },
        {
            "train_id": "402938",
            "model_series": "A",
            "model_number": "218",
            "max_speed": 120,
            "seat_count": 80,
            "toilet_count": 4,
            "reclining_seats": False,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": False,
        },
        {
            "train_id": "429844",
            "model_series": "A",
            "model_number": "121",
            "max_speed": 170,
            "seat_count": 80,
            "toilet_count": 5,
            "reclining_seats": False,
            "folding_tables": False,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": True,
        },
        {
            "train_id": "411827",
            "model_series": "A",
            "model_number": "109",
            "max_speed": 150,
            "seat_count": 60,
            "toilet_count": 6,
            "reclining_seats": True,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": False,
        },
        {
            "train_id": "428930",
            "model_series": "S",
            "model_number": "348",
            "max_speed": 90,
            "seat_count": 50,
            "toilet_count": 6,
            "reclining_seats": False,
            "folding_tables": False,
            "disability_access": False,
            "luggage_storage": True,
            "vending_machines": False,
            "food_service": False,
        },
        {
            "train_id": "445382",
            "model_series": "S",
            "model_number": "436",
            "max_speed": 100,
            "seat_count": 60,
            "toilet_count": 5,
            "reclining_seats": True,
            "folding_tables": False,
            "disability_access": False,
            "luggage_storage": False,
            "vending_machines": True,
            "food_service": False,
        },
        {
            "train_id": "409382",
            "model_series": "A",
            "model_number": "197",
            "max_speed": 160,
            "seat_count": 80,
            "toilet_count": 5,
            "reclining_seats": False,
            "folding_tables": True,
            "disability_access": True,
            "luggage_storage": True,
            "vending_machines": False,
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
        ("451621", "Ramoh", 0, date(2026, 10, 1), "Full interior cleaning", "Routine sanitation and seat inspection."),
        ("451621", "Khitsu", 1, date(2026, 10, 15), "Brake disc replacement", "Replaced front bogie brake pads and discs."),
        ("428930", "Itson", 2, date(2026, 10, 10), "Engine oil change", "Standard lubrication and filter swap."),
        ("402938", "Wand", 0, date(2026, 10, 20), "Electrical diagnostics", "Tested cabin lighting, doors, and HVAC."),
        ("429844", "Khitsu", 1, date(2026, 11, 2), "Suspension calibration", "Adjusted air suspension pressure."),
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
