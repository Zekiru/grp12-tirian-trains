from django.db import models

GENDER = [
    (0, 'Male'),
    (1, 'Female'),
]


class Customer(models.Model):
    # no id since maintenance_crew doesn't seem to have an id either but that can be changed
    customer_firstname = models.CharField(max_length=255)
    customer_lastname = models.CharField(max_length=255)
    middle_initial = models.CharField(max_length=1)
    birth_date = models.DateField()
    gender = models.IntegerField(
        choices=GENDER,
        default=0
    )

    def __str__(self):
        return (
            f"{self.customer_firstname} {self.middle_initial}. {self.customer_lastname}"
        )

    class Meta:
        ordering = ['customer_lastname', 'customer_firstname']
        verbose_name = 'Customer'
        verbose_name = 'Customers'


class Ticket(models.Model):
    ticket_id = models.CharField(
        max_length=8,
        unique=True
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    purchase_date = models.DateField()
    total_cost = models.IntegerField()
    # would be better to derive total_cost but im not gonna worry abt that rn

    def __str__(self):
        return (
            f"{self.ticket_id}"
        )

    class Meta:
        ordering = ['ticket_id']
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'


class TicketItinerary(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='ticket_itineraries'
    )
    schedule = models.ForeignKey(
        TripSchedule,  # idk if this will work since it's not defined in this view
        on_delete=models.PROTECT,
        related_name='ticket_itineraries'
    )
    schedule = models.IntegerField(
        default=1
    )

    def __str__(self):
        return (
            f"Ticket #{self.ticket} - Schedule #{self.schedule}"
        )

    class Meta:
        ordering = ['ticket', 'schedule']
        verbose_name = 'itinerary'
        verbose_name_plural = 'itineraries'
