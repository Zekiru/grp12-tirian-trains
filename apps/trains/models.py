from django.db import models

CONDITION = [
    (0, 'Excellent'),
    (1, 'Very Good'),
    (2, 'Good'),
    (3, 'Fair'),
    (4, 'Poor'),
]


class Train(models.Model):
    model_series = models.CharField(max_length = 3)
    model_number = models.CharField(max_length = 3)
    max_speed = models.PositiveIntegerField()
    seat_count = models.PositiveIntegerField()
    toilet_count = models.PositiveIntegerField()
    reclining_seats = models.BooleanField(default = False)
    folding_tables = models.BooleanField(default = False)
    disability_access = models.BooleanField(default = False)
    luggage_storage = models.BooleanField(default = False)
    vending_machines = models.BooleanField(default = False)
    food_service = models.BooleanField(default = False)

    def __str__(self):
        return (
            f"{self.pk} ({self.model_series}-{self.model_number})"
        )

    class Meta:
        ordering = ['id']
        verbose_name = 'train'
        verbose_name_plural = 'trains'


class MaintenanceCrew(models.Model):
    crew_firstname = models.CharField(max_length = 255)
    crew_lastname = models.CharField(max_length = 255)

    def __str__(self):
        first_initial = (self.crew_firstname or "")[:1]
        return f"{first_initial}. {self.crew_lastname}"


class Maintenance(models.Model):
    train = models.ForeignKey(
        Train, 
        on_delete = models.CASCADE, 
        related_name = 'maintenance_logs'
    )
    crew = models.ForeignKey(
        MaintenanceCrew, 
        on_delete = models.PROTECT, 
        related_name = 'maintenance_logs'
    )
    condition = models.IntegerField(
        choices = CONDITION,
        default = 0
    )
    maintenance_date = models.DateField()
    task = models.TextField(
        blank = True,
        default = ""
    )

    def __str__(self):
        return (
            f"Train {self.train} - Log #{self.pk} ({self.maintenance_date})"
        )

    class Meta:
        ordering = ['-maintenance_date']
        verbose_name = 'maintenance'
        verbose_name_plural = 'maintenance'
