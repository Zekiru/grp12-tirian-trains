from django.contrib import admin
from .models import (
    Train,
    MaintenanceCrew,
    Maintenance
)


class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 0
    fields = (
        'maintenance_date',
        'crew',
        'condition',
        'task',
        'description'
    )
    autocomplete_fields = ('crew',)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_filter = (
        'model_series',
        'disability_access',
        'food_service'
    )
    search_fields = (
        'train_id',
        'model_series',
        'model_number'
    )
    inlines = [MaintenanceInline]


@admin.register(MaintenanceCrew)
class MaintenanceCrewAdmin(admin.ModelAdmin):
    search_fields = (
        'crew_firstname',
        'crew_lastname'
    )


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_filter = (
        'condition',
        'maintenance_date'
    )
    list_select_related = ('train', 'crew')
    search_fields = (
        'train__model_series',
        'train__model_number',
        'crew__crew_lastname',
        'task',
        'description'
    )
