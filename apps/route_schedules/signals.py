from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ASeries, ASeriesLink, RouteStation, SSeries


@receiver([post_save, post_delete], sender=RouteStation)
def sync_station_series_records(sender, instance, **kwargs):
    station = instance.station

    if station.is_a_series:
        ASeries.objects.get_or_create(a_station=station)
    else:
        ASeries.objects.filter(a_station=station).delete()

    if not station.is_s_series:
        SSeries.objects.filter(s_station=station).delete()


@receiver(post_save, sender=ASeriesLink)
def sync_bidirectional_a_series_links(sender, instance, **kwargs):
    if instance.bidirectional:
        already_synced = ASeriesLink.objects.filter(
            a_origin=instance.a_destination,
            a_destination=instance.a_origin,
            travel_cost=instance.travel_cost,
            travel_duration=instance.travel_duration,
            bidirectional=True,
        ).exists()

        if not already_synced:
            ASeriesLink.objects.update_or_create(
                a_origin=instance.a_destination,
                a_destination=instance.a_origin,
                defaults={
                    "travel_cost": instance.travel_cost,
                    "travel_duration": instance.travel_duration,
                    "bidirectional": True,
                },
            )
    else:
        ASeriesLink.objects.filter(
            a_origin=instance.a_destination,
            a_destination=instance.a_origin,
        ).delete()


@receiver(post_delete, sender=ASeriesLink)
def delete_bidirectional_a_series_link(sender, instance, **kwargs):
    if instance.bidirectional:
        ASeriesLink.objects.filter(
            a_origin=instance.a_destination,
            a_destination=instance.a_origin,
        ).delete()
