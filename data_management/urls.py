from django.urls import path
from . import views

app_name = 'data_management'

urlpatterns = [
    path('', views.historical_data_view, name='historical_data'),
    path('download_template/<str:template_type>/', views.download_excel_template, name='download_template'),
    path('income_statement/', views.income_statement_view, name='income_statement'),
    path('export/income_statement/', views.export_income_statement_excel, name='export_income_statement_excel'),
    path('balance_sheet/', views.balance_sheet_view, name='balance_sheet'),
    path('export/balance_sheet/', views.export_balance_sheet_excel, name='export_balance_sheet_excel'),
    # ADDED New Cash Flow URLs
    path('cash_flow/', views.cash_flow_view, name='cash_flow'),
    path('export/cash_flow/', views.export_cash_flow_excel, name='export_cash_flow_excel'),
]