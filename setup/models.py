from django.db import models

class RSAFund(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="PENCOM Fund Name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RSA Fund (PENCOM)"
        verbose_name_plural = "RSA Funds (PENCOM)"

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nigerian State")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "State (Nigeria)"
        verbose_name_plural = "States (Nigeria)"

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=150, verbose_name="Location Name")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='locations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'state')
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.name}, {self.state.name}"

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Region Name")
    states = models.ManyToManyField(State, blank=True, related_name='regions')
    locations = models.ManyToManyField(Location, blank=True, related_name='regions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return self.name

class ManagedFund(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Managed Fund Name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Managed Fund"
        verbose_name_plural = "Managed Funds"

    def __str__(self):
        return self.name

class DateDetail(models.Model):
    date = models.DateField(unique=True)
    month = models.PositiveSmallIntegerField(editable=False)
    quarter = models.PositiveSmallIntegerField(editable=False)
    half_year = models.PositiveSmallIntegerField(editable=False)
    year = models.PositiveSmallIntegerField(editable=False)

    def save(self, *args, **kwargs):
        self.month = self.date.month
        self.year = self.date.year
        self.quarter = (self.date.month - 1) // 3 + 1
        self.half_year = 1 if self.date.month <= 6 else 2
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Date Detail"
        verbose_name_plural = "Date Table"
        ordering = ['date']

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} (Q{self.quarter}, H{self.half_year})"