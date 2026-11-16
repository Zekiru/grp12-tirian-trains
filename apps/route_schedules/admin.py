from django.contrib import admin
from .models import (
    ASeries,
    ASeriesLink,
    Route,
    RouteStation,
    SSeries,
    TrainStation,
    TripSchedule,
)


# --- Inlines ---

class RouteStationInline(admin.TabularInline):
    model = RouteStation
    extra = 1
    autocomplete_fields = ["station"]


class SSeriesInline(admin.TabularInline):
    model = SSeries
    extra = 0
    max_num = 1


class ASeriesInline(admin.TabularInline):
    model = ASeries
    extra = 0
    max_num = 1


class ASeriesLinkOriginInline(admin.TabularInline):
    model = ASeriesLink
    fk_name = "a_origin"
    extra = 1
    verbose_name = "Outgoing A-Series Link"
    verbose_name_plural = "Outgoing A-Series Links"


# --- ModelAdmins ---

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "fixed_cost", "fixed_travel_duration")
    search_fields = ("route_name",)
    inlines = [RouteStationInline]


@admin.register(TrainStation)
class TrainStationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_s_series", "is_a_series")
    search_fields = ("station_name",)
    inlines = [SSeriesInline, ASeriesInline]

    @admin.display(boolean=True, description="S-Series")
    def is_s_series(self, obj):
        return obj.is_s_series

    @admin.display(boolean=True, description="A-Series")
    def is_a_series(self, obj):
        return obj.is_a_series


@admin.register(RouteStation)
class RouteStationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "route", "station")
    list_filter = ("route",)
    search_fields = ("route__route_name", "station__station_name")
    autocomplete_fields = ["route", "station"]


@admin.register(SSeries)
class SSeriesAdmin(admin.ModelAdmin):
    list_display = ("__str__", "route_order")
    ordering = ("route_order",)
    search_fields = ("s_station__station_name",)
    autocomplete_fields = ["s_station"]


@admin.register(ASeries)
class ASeriesAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("a_station__station_name",)
    autocomplete_fields = ["a_station"]
    inlines = [ASeriesLinkOriginInline]


@admin.register(ASeriesLink)
class ASeriesLinkAdmin(admin.ModelAdmin):
    list_display = ("__str__", "travel_cost", "travel_duration")
    list_filter = ("a_origin", "a_destination")
    search_fields = (
        "a_origin__a_station__station_name",
        "a_destination__a_station__station_name",
    )


@admin.register(TripSchedule)
class TripScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "train",
        "departure_time",
        "arrival_time",
        "trip_duration",
        "trip_cost",
    )
    list_filter = ("trip_date", "route", "train")
    search_fields = (
        "route__route_name",
        "origin_station__station_name",
        "destination_station__station_name",
    )
    date_hierarchy = "trip_date"
    readonly_fields = ("trip_duration",)
    autocomplete_fields = ["route", "origin_station", "destination_station"]
