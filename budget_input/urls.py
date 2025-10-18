# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/budget_input/urls.py
from django.urls import path
from . import views

app_name = 'budget_input'

urlpatterns = [
    # Main Dashboard for Submissions
    path('', views.submission_index_view, name='submission_index'),
    
    # Assumption Management 
    path('assumptions/', views.assumption_dashboard_view, name='assumption_dashboard'),
    
    # Submission Forms
    path('submit/opex/', views.submit_budget_view, {'submission_type': 'opex'}, name='submit_opex'),
    path('submit/capex/', views.submit_budget_view, {'submission_type': 'capex'}, name='submit_capex'),
    path('submit/pin_data/', views.submit_budget_view, {'submission_type': 'pindata'}, name='submit_pin_data'),
    
    # --- NEW: Forecast Generation URLs ---
    #path('forecast/income_statement/', views.generate_forecast_view, {'report_type': 'income_statement'}, name='forecast_income_statement'),
    #path('forecast/', views.forecast_dashboard_view, name='forecast_dashboard'),
    #path('forecast/balance_sheet/', views.generate_forecast_view, {'report_type': 'balance_sheet'}, name='forecast_balance_sheet'),
    #path('forecast/cash_flow/', views.generate_forecast_view, {'report_type': 'cash_flow'}, name='forecast_cash_flow'),
    # --- UPDATED: Single Forecast Dashboard URL ---
    path('forecast/', views.forecast_dashboard_view, name='forecast_dashboard'),
    # --- NEW: Forecast Approval Endpoint ---
    path('forecast/submit/', views.submit_forecast_for_approval_view, name='submit_forecast_approval')
]