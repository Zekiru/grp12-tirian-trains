from datetime import timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Func, GeneratedField, Q, TimeField

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.trains.models import Train


class Route(models.Model):
    route_name = models.CharField(
        max_length=255,
        primary_key=True,
    )
    fixed_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    fixed_travel_duration = models.DurationField(
        null=True,
        blank=True,
        validators=[MinValueValidator(timedelta(0))],
    )

    def __str__(self):
        return self.route_name

    class Meta:
        ordering = ["route_name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(fixed_cost__gte=Decimal("0.00")) | Q(fixed_cost__isnull=True),
                name="route_fixed_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=Q(fixed_travel_duration__gte=timedelta(0)) | Q(fixed_travel_duration__isnull=True),
                name="route_fixed_duration_nonneg",
            ),
        ]
        verbose_name = "route"
        verbose_name_plural = "routes"


class TrainStation(models.Model):
    station_name = models.CharField(
        max_length=255,
        unique=True,
    )

    @property
    def is_s_series(self):
        return self.routes.filter(route_id="S-Series").exists()

    @property
    def is_a_series(self):
        return self.routes.filter(route_id="A-Series").exists()

    def __str__(self):
        return self.station_name

    class Meta:
        ordering = ["id"]
        verbose_name = "train station"
        verbose_name_plural = "train stations"


class RouteStation(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name="stations",
    )
    station = models.ForeignKey(
        TrainStation,
        on_delete=models.CASCADE,
        related_name="routes",
    )

    def __str__(self):
        return f"{self.station} ({self.route})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["route", "station"],
                name="unique_route_station",
            ),
        ]
        verbose_name = "route station"
        verbose_name_plural = "route stations"


class SSeries(models.Model):
    s_station = models.OneToOneField(
        TrainStation,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="s_series",
    )
    route_order = models.PositiveIntegerField(
        unique=True
    )

    def __str__(self):
        return self.s_station.station_name

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(route_order__gte=1),
                name="s_series_route_order_gte_1",
            ),
        ]
        verbose_name = "s series"
        verbose_name_plural = "s series"


class ASeries(models.Model):
    a_station = models.OneToOneField(
        TrainStation,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="a_series",
    )

    def __str__(self):
        return self.a_station.station_name

    class Meta:
        verbose_name = "a series"
        verbose_name_plural = "a series"


class ASeriesLink(models.Model):
    a_origin = models.ForeignKey(
        ASeries,
        on_delete=models.CASCADE,
        related_name="origin_links",
    )
    a_destination = models.ForeignKey(
        ASeries,
        on_delete=models.CASCADE,
        related_name="destination_links",
    )
    travel_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    travel_duration = models.DurationField(
        validators=[MinValueValidator(timedelta(0))],
    )

    def __str__(self):
        return f"{self.a_origin} to {self.a_destination}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["a_origin", "a_destination"],
                name="unique_a_origin_destination",
            ),
            models.CheckConstraint(
                condition=Q(travel_cost__gte=Decimal("0.00")),
                name="travel_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=Q(travel_duration__gte=timedelta(0)),
                name="travel_duration_nonneg",
            ),
            models.CheckConstraint(
                condition=~Q(a_origin=F("a_destination")),
                name="invalid_link",
            ),
        ]
        verbose_name = "a series link"
        verbose_name_plural = "a series links"


class TripSchedule(models.Model):
    train = models.ForeignKey(
        Train,
        on_delete=models.PROTECT,
        related_name="trip_schedules",
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name="trip_schedules",
    )
    origin_station = models.ForeignKey(
        TrainStation,
        on_delete=models.PROTECT,
        related_name="departing_trips",
    )
    destination_station = models.ForeignKey(
        TrainStation,
        on_delete=models.PROTECT,
        related_name="arriving_trips",
    )
    trip_date = models.DateField()
    departure_time = TimeField()
    arrival_time = TimeField()
    trip_duration = models.DurationField(editable=False)
    trip_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def save(self, *args, **kwargs):
        dep_td = timedelta(
            hours=self.departure_time.hour,
            minutes=self.departure_time.minute,
            seconds=self.departure_time.second,
            microseconds=self.departure_time.microsecond,
        )
        arr_td = timedelta(
            hours=self.arrival_time.hour,
            minutes=self.arrival_time.minute,
            seconds=self.arrival_time.second,
            microseconds=self.arrival_time.microsecond,
        )
        self.trip_duration = arr_td - dep_td if arr_td >= dep_td else (arr_td - dep_td) + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route}: {self.origin_station} -> {self.destination_station} ({self.trip_date})"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(trip_cost__gte=Decimal("0.00")),
                name="trip_cost_nonneg",
            ),
            models.CheckConstraint(
                condition=~Q(origin_station=F("destination_station")),
                name="invalid_origin_destination",
            ),
        ]
        verbose_name = "trip schedule"
        verbose_name_plural = "trip schedules"


# Auto-Sync Signal for [S/A]-Series

@receiver([post_save, post_delete], sender=RouteStation)
def sync_station_series_records(sender, instance, **kwargs):
    station = instance.station

    # Auto-create or delete ASeries record based on 'A-Series' route membership
    if station.is_a_series:
        ASeries.objects.get_or_create(a_station=station)
    else:
        ASeries.objects.filter(a_station=station).delete()

    # Auto-delete SSeries record if removed from 'S-Series' route
    if not station.is_s_series:
        SSeries.objects.filter(s_station=station).delete()

