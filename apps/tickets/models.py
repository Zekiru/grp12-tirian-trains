from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.route_schedules.models import TripSchedule

GENDER = [
    (0, "Male"),
    (1, "Female"),
]


class Customer(models.Model):
    customer_firstname = models.CharField(max_length=255)
    customer_lastname = models.CharField(max_length=255)
    middle_initial = models.CharField(max_length=1, blank=True, default="")
    birth_date = models.DateField()
    gender = models.IntegerField(choices=GENDER, default=0)

    def __str__(self):
        mid = f" {self.middle_initial}." if self.middle_initial else ""
        return f"{self.customer_firstname}{mid} {self.customer_lastname}"

    class Meta:
        ordering = ["customer_lastname", "customer_firstname"]
        verbose_name = "customer"
        verbose_name_plural = "customers"
        constraints = [
            models.UniqueConstraint(
                fields=["customer_firstname", "middle_initial", "customer_lastname", "birth_date"],
                name="unique_customer_identity",
            )
        ]


class Ticket(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    purchase_date = models.DateField(default=timezone.localdate)
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    def recalculate_total_cost(self):
        total = (
            self.ticket_itineraries.aggregate(total=Sum("schedule__trip_cost"))["total"]
            or Decimal("0.00")
        )
        Ticket.objects.filter(pk=self.pk).update(total_cost=total)
        self.total_cost = total

    def __str__(self):
        return f"Ticket #{self.pk}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_cost__gte=0),
                name="total_cost_gte_0",
            )
        ]
        ordering = ["id"]
        verbose_name = "ticket"
        verbose_name_plural = "tickets"


class TicketItinerary(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="ticket_itineraries",
    )
    schedule = models.ForeignKey(
        TripSchedule,
        on_delete=models.PROTECT,
        related_name="ticket_itineraries",
    )
    trip_order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.ticket} (Leg {self.trip_order}) - {self.schedule}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ticket", "schedule"],
                name="unique_ticket_schedule",
            ),
            models.UniqueConstraint(
                fields=["ticket", "trip_order"],
                name="unique_ticket_trip_order",
            ),
            models.CheckConstraint(
                condition=models.Q(trip_order__gte=1),
                name="trip_order_gte_1",
            ),
        ]
        ordering = ["ticket", "trip_order"]
        verbose_name = "ticket itinerary"
        verbose_name_plural = "ticket itineraries"
