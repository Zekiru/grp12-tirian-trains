from django.contrib import admin
from .models import (
    Train,
    MaintenanceCrew,
    Maintenance
)


class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 1
    fields = ('maintenance_date', 'crew', 'condition', 'task')
    autocomplete_fields = ('crew',)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    # list_display = ('train_id', 'model_series', 'model_number', 'max_speed', 'seat_count')
    list_filter = ('model_series', 'disability_access', 'food_service')
    search_fields = ('train_id', 'model_series', 'model_number')
    inlines = [MaintenanceInline]


@admin.register(MaintenanceCrew)
class MaintenanceCrewAdmin(admin.ModelAdmin):
    # list_display = ('id', 'crew_firstname', 'crew_lastname')
    search_fields = ('crew_firstname', 'crew_lastname')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    # list_display = ('id', 'train', 'crew', 'condition', 'maintenance_date')
    list_filter = ('condition', 'maintenance_date')
    list_select_related = ('train', 'crew')
    search_fields = (
        'train__model_series',
        'train__model_number',
        'crew__crew_lastname',
        'task',
    )
