from django.db import models
from apps.trains.models import Train
from django.db.models import F, Func, Q, GeneratedField, TimeField


class Route(models.Model):
    route_name = models.CharField(max_length=255, primary_key=True)
    fixed_cost = models.IntegerField(null=True, blank=True)
    fixed_travel_duration = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.route_name}"
        )

    class Meta:
        db_table = "ROUTE"
        constraints = [
            models.CheckConstraint(
                condition=Q(fixed_cost__gte=0),
                name="chk_route_fixed_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=Q(fixed_travel_duration__gte=0),
                name="chk_route_fixed_duration_nonneg",
            ),
        ]
        ordering = ['route_name']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'


class TrainStation(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_name = models.CharField(max_length=255, unique=True)
    s = models.BooleanField(default=False)
    a = models.BooleanField(default=False)

    @property
    def is_s_series(self):
        return hasattr(self, "s_series")

    @property
    def is_a_series(self):
        return hasattr(self, "a_series")

    class Meta:
        db_table = "TRAIN_STATION"
        ordering = ['station_id']
        verbose_name = 'Train Station'
        verbose_name_plural = 'Train Stations'


class RouteStation(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        db_column="route_name",
        related_name="route_stations",
    )
    station = models.ForeignKey(
        TrainStation,
        on_delete=models.PROTECT,
        db_column="station_id",
        related_name="route_stations",
    )
    pk = models.CompositePrimaryKey("route", "station")

    class Meta:
        db_table = "ROUTE_STATION"
        verbose_name = 'Route Station'
        verbose_name_plural = 'Route Stations'


class SSeries(models.Model):
    s_station = models.OneToOneField(
        TrainStation,
        on_delete=models.PROTECT,
        primary_key=True,
        db_column="s_station_id",
        related_name="s_series",
    )
    route_order = models.IntegerField()

    class Meta:
        db_table = "S_SERIES"
        constraints = [
            models.CheckConstraint(
                condition=Q(route_order__gte=1),
                name="chk_s_series_route_order",
            ),
        ]
        verbose_name = 'S Series'



class ASeries(models.Model):
    a_station = models.OneToOneField(
        TrainStation,
        on_delete=models.PROTECT,
        primary_key=True,
        db_column="a_station_id",
        related_name="a_series",
    )

    class Meta:
        db_table = "A_SERIES"
        verbose_name = 'A Series'



class ASeriesLink(models.Model):
    a_origin = models.ForeignKey(
        ASeries,
        on_delete=models.PROTECT,
        db_column="a_origin_id",
        related_name="origin_links",
    )
    a_destination = models.ForeignKey(
        ASeries,
        on_delete=models.PROTECT,
        db_column="a_destination_id",
        related_name="destination_links",
    )
    travel_cost = models.DecimalField(max_digits=10, decimal_places=2)
    travel_duration = models.IntegerField()
    pk = models.CompositePrimaryKey("a_origin", "a_destination")

    class Meta:
        db_table = "A_SERIES_LINK"
        constraints = [
            models.CheckConstraint(
                condition=Q(travel_cost__gte=0),
                name="chk_link_travel_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=Q(travel_duration__gte=0),
                name="chk_link_travel_duration_nonneg",
            ),
            models.CheckConstraint(
                condition=~Q(a_origin=F("a_destination")),
                name="chk_link",
            ),
        ]


class TripSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    train = models.ForeignKey(
        Train,
        on_delete=models.PROTECT,
        db_column="train_id",
        related_name="trip_schedules",
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        db_column="route_name",
        related_name="trip_schedules",
    )
    origin_station = models.ForeignKey(
        TrainStation,
        on_delete=models.PROTECT,
        db_column="origin_station_id",
        related_name="departing_trips",
    )
    destination_station = models.ForeignKey(
        TrainStation,
        on_delete=models.PROTECT,
        db_column="destination_station_id",
        related_name="arriving_trips",
    )
    trip_date = models.DateField()
    departure_time = TimeField()
    arrival_time = TimeField()
    trip_duration = GeneratedField(
        expression=Func(
            F("arrival_time"),
            F("departure_time"),
            function="TIMEDIFF",
        ),
        output_field=TimeField(),
        db_persist=True,
    )
    trip_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "TRIP_SCHEDULE"
        constraints = [
            models.CheckConstraint(
                condition=Q(trip_cost__gte=0),
                name="chk_trip_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=~Q(origin_station=F("destination_station")),
                name="chk_origin_destination",
            ),
        ]
        verbose_name = 'Trip Schedule'
