from django.urls import path
from . import views

app_name = 'aum_management'

urlpatterns = [
    # Main AUM Calculation tab (renamed from aum_dashboard)
    path('', views.aum_calculation_view, name='aum_calculation'),
    
    # New Views for separate tabs/sections
    path('drivers/', views.aum_drivers_view, name='aum_drivers'),
    path('rsa_historical/', views.rsa_historical_view, name='rsa_historical'),
    path('managed_fund_historical/', views.managed_fund_historical_view, name='managed_fund_historical'),
]