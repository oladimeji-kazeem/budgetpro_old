# predictive_analytics/urls.py
from django.urls import path
from . import views

app_name = 'predictive_analytics'

urlpatterns = [
    # Main Index
    path('', views.analytics_index_view, name='analytics_index'),
    
    # Sub-modules
    path('financial_forecasting/', views.financial_forecasting_view, name='financial_forecasting'),
    path('budget_management/', views.budget_management_view, name='budget_management'),
    path('customer_insight/', views.customer_insight_view, name='customer_insight'),
]