from django.contrib import admin
from .models import (
    Customer,
    Ticket,
    TicketItinerary,
)
# Register your models here.
class TicketItineraryInline(admin.TabularInline):
    model = TicketItinerary
    extra = 0
    fields = (
        'schedule',
        'trip_order',
    )
    autocomplete_fields = ('schedule',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'customer_firstname', 
        'customer_lastname', 
        'birth_date', 
        'gender',
    )
    list_filter = (
        'gender',
    )
    search_fields = (
        'customer_lastname',
        'customer_firstname',
    )

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id', 
        'customer', 
        'purchase_date', 
        'total_cost'
    )
    list_filter = (
        'purchase_date',
    )
    search_fields = (
        'ticket_id',
        'customer__customer_lastname',
        'customer__customer_firstname',
    )
    inlines = [TicketItineraryInline]

@admin.register(TicketItinerary)
class TicketItineraryAdmin(admin.ModelAdmin):
    list_display = (
        'ticket',
        'schedule',
        'trip_order'
    )
    list_filter = (
        'trip_order',
    )
    list_select_related = ('ticket', 'schedule')
    search_fields = (
        'ticket__ticket_id',
        'trip_order',
    )