from django.contrib import admin
from .models import Customer, Ticket, TicketItinerary


class TicketItineraryInline(admin.TabularInline):
    model = TicketItinerary
    extra = 1
    fields = ("trip_order", "schedule")
    ordering = ("trip_order",)
    autocomplete_fields = ("schedule",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "birth_date", "gender")
    list_filter = ("gender",)
    search_fields = ("customer_lastname", "customer_firstname")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("__str__", "customer", "purchase_date", "total_cost")
    list_filter = ("purchase_date",)
    search_fields = ("id", "customer__customer_lastname", "customer__customer_firstname")
    autocomplete_fields = ("customer",)
    readonly_fields = ("total_cost",)
    inlines = [TicketItineraryInline]


@admin.register(TicketItinerary)
class TicketItineraryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "ticket", "trip_order", "schedule")
    list_filter = ("trip_order",)
    list_select_related = ("ticket", "schedule")
    ordering = ("ticket", "trip_order")
    autocomplete_fields = ("ticket", "schedule")
    search_fields = (
        "ticket__id",
        "schedule__origin_station__station_name",
        "schedule__destination_station__station_name",
    )
