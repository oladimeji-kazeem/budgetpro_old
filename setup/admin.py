from django.contrib import admin
from .models import RSAFund, State, Location, Region, ManagedFund, DateDetail

@admin.register(RSAFund)
class RSAFundAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'created_at')
    list_filter = ('state',)
    search_fields = ('name', 'state__name')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('states', 'locations')
    search_fields = ('name',)

@admin.register(ManagedFund)
class ManagedFundAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(DateDetail)
class DateDetailAdmin(admin.ModelAdmin):
    list_display = ('date', 'month', 'quarter', 'half_year', 'year')
    list_filter = ('year', 'quarter', 'half_year')
    search_fields = ('date',)
    ordering = ('date',)
    readonly_fields = ('month', 'quarter', 'half_year', 'year')