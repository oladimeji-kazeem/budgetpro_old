from django.urls import path
from . import views

app_name = 'aum_management'

urlpatterns = [
    path('', views.aum_dashboard_view, name='aum_dashboard'),
    # Additional AUM links can be added here if needed
]