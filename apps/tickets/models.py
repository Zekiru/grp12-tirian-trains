from django.db import models
# from apps.route_schedules.models import TripSchedule

# GENDER = [
#     (0, 'Male'),
#     (1, 'Female'),
# ]


# class Customer(models.Model):
#     # no id since maintenance_crew doesn't seem to have an id either but that can be changed
#     customer_firstname = models.CharField(max_length=255)
#     customer_lastname = models.CharField(max_length=255)
#     middle_initial = models.CharField(max_length=1)
#     birth_date = models.DateField()
#     gender = models.IntegerField(
#         choices=GENDER,
#         default=0
#     )

#     def __str__(self):
#         return (
#             f"{self.customer_firstname} {self.middle_initial}. {self.customer_lastname}"
#         )

#     class Meta:
#         ordering = ['customer_lastname', 'customer_firstname']
#         verbose_name = 'Customer'
#         verbose_name_plural = 'Customers'


# class Ticket(models.Model):
#     ticket_id = models.CharField(
#         max_length=8,
#         unique=True
#     )
#     customer = models.ForeignKey(
#         Customer,
#         on_delete=models.CASCADE,
#         related_name='tickets'
#     )
#     purchase_date = models.DateField()
#     total_cost = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         default=0.00
#     )
#     # would be better to derive total_cost but im not gonna worry abt that rn
#     # will try to figure out later as well

#     def __str__(self):
#         return (
#             f"{self.ticket_id}"
#         )

#     class Meta:
#         constraints = [
#             models.CheckConstraint(
#                 condition=  models.Q(total_cost__gte=0),
#                 name='total_cost_gte_0'
#             )
#         ]
#         ordering = ['ticket_id']
#         verbose_name = 'ticket'
#         verbose_name_plural = 'tickets'


# class TicketItinerary(models.Model):
#     ticket = models.ForeignKey(
#         Ticket,
#         on_delete=models.CASCADE,
#         related_name='ticket_itineraries'
#     )
#     schedule = models.ForeignKey(
#         TripSchedule,  # idk if this will work since it's not defined in this view
#         on_delete=models.PROTECT,
#         related_name='ticket_itineraries'
#     )
#     trip_order = models.IntegerField(
#         default=1
#     )

#     def __str__(self):
#         return (
#             f"Ticket #{self.ticket} - Schedule #{self.schedule}"
#         )

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['ticket', 'schedule'],
#                 name='unique_ticket_schedule'
#             )
#         ] #just to make sure ticket doesnt have same sched twice
#         ordering = ['ticket', 'schedule']
#         verbose_name = 'itinerary'
#         verbose_name_plural = 'itineraries'
