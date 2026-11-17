from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Ticket, TicketItinerary


@receiver([post_save, post_delete], sender=TicketItinerary)
def update_ticket_total_cost(sender, instance, **kwargs):
    """Recalculate Ticket.total_cost whenever a TicketItinerary leg is added, updated, or removed."""
    if Ticket.objects.filter(pk=instance.ticket_id).exists():
        instance.ticket.recalculate_total_cost()
