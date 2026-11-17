# 4/5
from datetime import date
from decimal import Decimal

from apps.route_schedules.models import TripSchedule
from apps.tickets.models import Customer, Ticket, TicketItinerary


def seed_tickets(trip_schedules: dict[str, TripSchedule]) -> None:
    """
    Seed the 11 customers, 11 tickets, and ordered multi-leg itineraries
    using the TripSchedule dictionary returned by seed_routes_and_schedules().
    Ticket.total_cost is automatically computed by the TicketItinerary signal.
    """
    print("SEED[4/5] Seeding customers, tickets, and itineraries...")

    # 1. Customers (11 Narnia/Tirian characters; keyed by readable slug -> Customer instance)
    customers_data = [
        ("lilia_vanrouge", "Lilia", "F", "Vanrouge", date(1959, 1, 1), 0),
        ("kishiar_la_orr", "Kishiar", "P", "La Orr", date(1983, 2, 9), 0),
        ("sooyoung_han", "Sooyoung", "O", "Han", date(1982, 4, 1), 1),
        ("dokja_kim", "Dokja", "R", "Kim", date(1989, 2, 15), 0),
        ("joonghuyk_yoo", "Joonghuyk", "V", "Yoo", date(1986, 8, 3), 0),
        ("soleum_kim", "Soleum", "G", "Kim", date(1987, 9, 13), 0),
        ("koharu_sakurada", "Koharu", "L", "Sakurada", date(1999, 3, 23), 1),
        ("kanna_hagiwara", "Kanna", "O", "Hagiwara", date(1987, 10, 1), 1),
        ("chiyo_tamaki", "Chiyo", "V", "Tamaki", date(1963, 2, 1), 1),
        ("ena_hasumii", "Ena", "E", "Hasumii", date(2002, 7, 3), 1),
        ("adam_grove", "Adam", "K", "Grove", date(1972, 6, 1), 0),
    ]

    customers: dict[str, Customer] = {}
    for slug, first_name, middle_initial, last_name, birth_date, gender in customers_data:
        customer, _ = Customer.objects.update_or_create(
            customer_firstname=first_name,
            middle_initial=middle_initial,
            customer_lastname=last_name,
            birth_date=birth_date,
            defaults={"gender": gender},
        )
        customer.full_clean()
        customers[slug] = customer

    # 2. Tickets & Ordered Itinerary Legs
    # Format: (customer_slug, purchase_date, [trip_schedule_keys_in_order])
    tickets_data = [
        # Multi-leg S-Series loop trip: Beaver's Dam -> Allies' Enclave -> The Wardrobe ($2.00 + $2.00 = $4.00)
        ("sooyoung_han", date(2026, 11, 14), ["s_dam_to_enclave", "s_enclave_to_wardrobe"]),
        # Multi-leg S-Series loop trip: Allies' Enclave -> The Wardrobe -> The Lamp Post ($2.00 + $2.00 = $4.00)
        ("adam_grove", date(2026, 11, 14), ["s_enclave_to_wardrobe", "s_wardrobe_to_lamppost"]),
        # Single-leg S-Series trip: The Lamp Post -> Beaver's Dam ($2.00)
        ("joonghuyk_yoo", date(2026, 11, 15), ["s_lamppost_to_dam"]),
        # Single-leg A-Series trip: Allies' Enclave -> Mr. Tumms ($8.00)
        ("kishiar_la_orr", date(2026, 11, 15), ["a_enclave_to_tumms"]),
        # Multi-leg A-Series trip: Allies' Enclave -> Dancing Lawn -> Anvard ($15.00 + $13.50 = $28.50)
        ("dokja_kim", date(2026, 11, 15), ["a_enclave_to_lawn", "a_lawn_to_anvard"]),
        # Cross-series transfer: S-Series (Beaver's Dam -> Allies' Enclave) + A-Series (Allies' Enclave -> Aslan's Camp) ($2.00 + $18.00 = $20.00)
        ("soleum_kim", date(2026, 11, 16), ["s_dam_to_enclave", "a_enclave_to_aslan"]),
        # Single-leg A-Series trip: Cauldron Pool -> Father Christmas ($9.50)
        ("ena_hasumii", date(2026, 11, 16), ["a_cauldron_to_christmas"]),
        # Single-leg A-Series trip: Witch's Camp -> The Stone Table ($8.50)
        ("chiyo_tamaki", date(2026, 11, 16), ["a_witch_to_stonetable"]),
        # Full 4-leg S-Series circular loop ($2.00 * 4 = $8.00)
        (
            "kanna_hagiwara",
            date(2026, 11, 14),
            ["s_dam_to_enclave", "s_enclave_to_wardrobe", "s_wardrobe_to_lamppost", "s_lamppost_to_dam"],
        ),
        # Second ticket for Kanna Hagiwara: Allies' Enclave -> Dancing Lawn ($15.00)
        ("kanna_hagiwara", date(2026, 11, 16), ["a_enclave_to_lawn"]),
        # Cross-series transfer for Koharu Sakurada: S-Series + A-Series ($2.00 + $8.00 = $10.00)
        ("koharu_sakurada", date(2026, 11, 16), ["s_dam_to_enclave", "a_enclave_to_tumms"]),
    ]

    for customer_slug, purchase_date, schedule_keys in tickets_data:
        customer = customers[customer_slug]
        ordered_schedules = [trip_schedules[key] for key in schedule_keys]
        target_legs = [(sched.pk, order) for order, sched in enumerate(ordered_schedules, start=1)]

        # Idempotent lookup: reuse existing ticket if customer, purchase_date, and ordered legs match
        ticket = next(
            (
                candidate
                for candidate in Ticket.objects.filter(customer=customer, purchase_date=purchase_date)
                if list(
                    candidate.ticket_itineraries.order_by("trip_order").values_list("schedule_id", "trip_order")
                )
                == target_legs
            ),
            None,
        )

        if ticket is None:
            ticket = Ticket.objects.create(
                customer=customer,
                purchase_date=purchase_date,
                total_cost=Decimal("0.00"),
            )
            ticket.full_clean()

        for trip_order, schedule in enumerate(ordered_schedules, start=1):
            itinerary, _ = TicketItinerary.objects.update_or_create(
                ticket=ticket,
                trip_order=trip_order,
                defaults={"schedule": schedule},
            )
            itinerary.full_clean()

    print(
        f"      OK - {Customer.objects.count()} Customers, "
        f"{Ticket.objects.count()} Tickets, "
        f"{TicketItinerary.objects.count()} TicketItineraries."
    )
