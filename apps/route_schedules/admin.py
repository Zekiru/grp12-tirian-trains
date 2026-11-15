from django.contrib import admin
from .models import (
    Route,
    SSeries,
    ASeries,
    TrainStation,
    TripSchedule,
)

# Register your models here.
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        'route_name', 
        'fixed_cost', 
        'fixed_travel_duration', 
    )
    list_filter = (
        'route_name', 
    )
    search_fields = (
        'route_name',
    )


class SSeriesInLine(admin.StackedInline):
    model = SSeries
    fk_name = 's_station'
    extra = 0


class ASeriesInLine(admin.StackedInline):
    model = ASeries
    fk_name = 'a_station'
    extra = 0


@admin.register(TrainStation)
class TrainStationAdmin(admin.ModelAdmin):
    list_display = (
        'station_id', 
        'station_name', 
        'in_s_series', 
        'in_a_series', 
    )
    list_filter = (
        'station_name', 
    )
    search_fields = (
        'station_name',
    )
    list_select_related = ('s_series', 'a_series')
    inlines = [SSeriesInLine, ASeriesInLine]

    @admin.display(boolean=True, description="S-series")
    def in_s_series(self, obj):
        return obj.is_s_series

    @admin.display(boolean=True, description="A-series")
    def in_a_series(self, obj):
        return obj.is_a_series
    

@admin.register(TripSchedule)
class TripScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'schedule_id',
        'train',
        'route',
        'origin_station', 
        'destination_station',
        'trip_date',
        'departure_time',
        'trip_duration',
        'trip_cost' 
    )
    list_filter = (
        'trip_date',
        'train', 
        'route',
        'origin_station', 
        'destination_station',
    )
    list_select_related = (
        'train', 
        'route',
        'origin_station', 
        'destination_station',
    )
    search_fields = (
        'route__route_name',
        'origin_station__station_name',
        'destination_station__station_name',
    )
    date_hierarchy = 'trip_date'
    readonly_fields = ('trip_duration',)


