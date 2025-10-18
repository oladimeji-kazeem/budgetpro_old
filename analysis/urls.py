# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/analysis/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.analysis_dashboard_view, name='analysis_dashboard'),
    # NEW: Specific Report URLs with a report_type parameter
    path('trends/', views.trend_dashboard_view, name='trend_dashboard'),
    path('report/income_statement/', views.analysis_report_view, {'report_type': 'income_statement'}, name='analysis_income_statement'),
    path('report/balance_sheet/', views.analysis_report_view, {'report_type': 'balance_sheet'}, name='analysis_balance_sheet'),
    path('report/cash_flow/', views.analysis_report_view, {'report_type': 'cash_flow'}, name='analysis_cash_flow'),
]