# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/analysis/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# FIX: Import REPORTING_PERIOD_CHOICES along with IncomeStatementFilterForm
from data_management.forms import IncomeStatementFilterForm, REPORTING_PERIOD_CHOICES 
import datetime
import random # Used for mocking variance figures
import json # NEW: To serialize data for JavaScript


def generate_mock_analysis_data():
    """Mocks the data based on the Analysis.xlsx - Sheet1.csv structure."""
    data = []
    current_date = datetime.date(2022, 1, 1)
    
    # Define the core metrics (simplified)
    metrics = [
        {'name': 'Return on Assets (ROA)', 'base_value': 0.08, 'is_percent': True},
        {'name': 'Return on Equity (ROE)', 'base_value': 0.12, 'is_percent': True},
        {'name': 'Profit Margin', 'base_value': 0.25, 'is_percent': True},
        {'name': 'Expense Ratio', 'base_value': 0.35, 'is_percent': True},
        {'name': 'AUM Growth Rate', 'base_value': 0.15, 'is_percent': True},
        {'name': 'Total Revenue (₦)', 'base_value': 1_200_000_000, 'is_percent': False},
        {'name': 'Closing AUM (₦)', 'base_value': 15_000_000_000, 'is_percent': False},
    ]

    for metric in metrics:
        # 'is_percent' flag is used in the template for formatting (e.g., 8.00% vs ₦1,200,000)
        metric_data = {'description': metric['name'], 'is_percent': metric['is_percent'], 'periods': {}}
        base = Decimal(metric['base_value'])
        
        # Generate 32 quarters (8 years: 2022-2029)
        temp_date = current_date
        for i in range(32):
            # Q1-2022, Q4-2022, etc.
            period_label = temp_date.strftime('Q%m-%Y') 
            
            # Mock quarterly data flow (simple 0.5% growth/reduction per quarter)
            if metric['is_percent']:
                value = base * (Decimal(1) + Decimal(0.005) * i) 
            elif 'Revenue' in metric['name']:
                value = base + Decimal(200_000_000) * i 
            elif 'AUM' in metric['name']:
                value = base + Decimal(500_000_000) * i 
            else:
                 value = base * (Decimal(1) - Decimal(0.002) * i)
                 
            metric_data['periods'][period_label] = value.quantize(Decimal('0.01')) if metric['is_percent'] else value.quantize(Decimal('0'))

            # Advance date by 3 months
            if temp_date.month == 10:
                 temp_date = temp_date.replace(year=temp_date.year + 1, month=1)
            else:
                temp_date = temp_date.replace(month=temp_date.month + 3)
                
        data.append(metric_data)

    return data

@login_required
def analysis_dashboard_view(request):
    # Reuse the existing filter form for consistency
    filter_form = IncomeStatementFilterForm(request.GET)
    
    # Mock data generation based on the CSV structure
    financial_data = generate_mock_analysis_data()
    
    # Extract unique period labels from the first item
    period_labels = list(financial_data[0]['periods'].keys()) if financial_data else []
    
    # Mock KPI cards (using the latest data)
    latest_data = {item['description']: list(item['periods'].values())[-1] for item in financial_data if item['periods']}
    
    performance_cards = [
        {'title': 'Closing AUM', 'value': f'₦{latest_data.get("Closing AUM (₦)", 0):,.0f}', 'change': '+1.5%', 'trend': 'up', 'icon': 'fas fa-chart-pie', 'color': 'success'},
        {'title': 'Profit Margin', 'value': f'{latest_data.get("Profit Margin", 0.0):.2%}', 'change': '+0.2%', 'trend': 'up', 'icon': 'fas fa-percentage', 'color': 'primary'},
        {'title': 'Return on Assets (ROA)', 'value': f'{latest_data.get("Return on Assets (ROA)", 0.0):.2%}', 'change': '+0.1%', 'trend': 'up', 'icon': 'fas fa-arrow-up', 'color': 'info'},
        {'title': 'Total Revenue', 'value': f'₦{latest_data.get("Total Revenue (₦)", 0):,.0f}', 'change': '+2.0%', 'trend': 'up', 'icon': 'fas fa-hand-holding-usd', 'color': 'warning'},
    ]
    
    context = {
        'filter_form': filter_form,
        'performance_cards': performance_cards,
        'financial_data': financial_data,
        'period_labels': period_labels,
        'report_type': 'Performance Analysis',
    }
    return render(request, 'analysis/analysis_dashboard.html', context)


def mock_generate_comparison_data(report_type):
    """Generates mock data comparing Actual vs Budget."""
    
    if report_type == 'income_statement':
        title = "Income Statement Analysis"
        report_data = [
            {'desc': 'Total Revenue', 'actual': 1200000000, 'budget': 1150000000, 'type': 'subtotal'},
            {'desc': 'Staff Costs', 'actual': 300000000, 'budget': 320000000, 'type': 'account'},
            {'desc': 'Admin Expenses', 'actual': 250000000, 'budget': 240000000, 'type': 'account'},
            {'desc': 'Total Operating Expenses', 'actual': 550000000, 'budget': 560000000, 'type': 'subtotal'},
            {'desc': 'Net Profit Before Tax', 'actual': 650000000, 'budget': 590000000, 'type': 'major_total'},
        ]
        kpis = [
            {'title': 'Budget Variance (NP)', 'value': '+10.17%', 'icon': 'fas fa-bullseye', 'color': 'success'},
            {'title': 'MoM Growth (NP)', 'value': '+2.5%', 'icon': 'fas fa-calendar-alt', 'color': 'primary'},
            {'title': 'YoY Growth (NP)', 'value': '+15.2%', 'icon': 'fas fa-chart-line', 'color': 'info'},
        ]
        
    elif report_type == 'balance_sheet':
        title = "Balance Sheet Analysis"
        report_data = [
            {'desc': 'Total Current Assets', 'actual': 1800000000, 'budget': 1750000000, 'type': 'header'},
            {'desc': 'Cash & Bank Balances', 'actual': 400000000, 'budget': 350000000, 'type': 'account'},
            {'desc': 'Total Assets', 'actual': 2800000000, 'budget': 2700000000, 'type': 'major_total'},
        ]
        kpis = [
            {'title': 'Current Ratio (Actual)', 'value': '2.1x', 'icon': 'fas fa-balance-scale', 'color': 'success'},
            {'title': 'Debt to Equity', 'value': '0.8x', 'icon': 'fas fa-arrows-alt-h', 'color': 'danger'},
            {'title': 'Asset Growth (YoY)', 'value': '+5.0%', 'icon': 'fas fa-chart-area', 'color': 'info'},
        ]
        
    elif report_type == 'cash_flow':
        title = "Cash Flow Analysis"
        report_data = [
            {'desc': 'Net Cash from Operating Activities', 'actual': 750000000, 'budget': 700000000, 'type': 'subtotal'},
            {'desc': 'Net Cash from Investing Activities', 'actual': -200000000, 'budget': -250000000, 'type': 'subtotal'},
            {'desc': 'Net Change in Cash', 'actual': 550000000, 'budget': 450000000, 'type': 'major_total'},
        ]
        kpis = [
            {'title': 'Total Cash Inflow Variance', 'value': '+20.0%', 'icon': 'fas fa-exchange-alt', 'color': 'success'},
            {'title': 'Cash Conversion Cycle', 'value': '45 Days', 'icon': 'fas fa-sync-alt', 'color': 'primary'},
            {'title': 'Ending Cash Balance', 'value': '₦1.2B', 'icon': 'fas fa-university', 'color': 'warning'},
        ]
    
    else:
        title = "Report Analysis"
        report_data = []
        kpis = []

    # Calculate variance and period change columns for the Income Statement
    if report_type == 'income_statement':
        for item in report_data:
            # Only apply comparison logic to financial lines
            if item['type'] in ['account', 'subtotal', 'major_total']:
                
                # Mock calculation and period changes
                actual = item['actual']
                budget = item['budget']
                variance = actual - budget
                variance_pct = (variance / budget) * 100 if budget else 0
                
                # Mock MoM/QoQ/YoY (random fluctuation around a base)
                mom = (random.randint(-1, 1) * 0.01 + 0.05) * 100 
                qoq = (random.randint(0, 2) * 0.01 + 0.10) * 100 
                yoy = (random.randint(1, 3) * 0.01 + 0.15) * 100 

                item.update({
                    'variance': Decimal(variance),
                    'variance_pct': Decimal(variance_pct),
                    'mom': Decimal(mom),
                    'qoq': Decimal(qoq),
                    'yoy': Decimal(yoy),
                })

    return title, report_data, kpis


@login_required
def analysis_report_view(request, report_type):
    """
    Renders the detailed financial analysis report (IS, BS, or CF) 
    with Actual vs. Budget comparison and period changes.
    """
    filter_form = IncomeStatementFilterForm(request.GET)
    
    # 1. Determine Report and Mock Data
    title, report_data, kpis = mock_generate_comparison_data(report_type)
    
    # 2. Handle Filters for display purposes
    applied_filters = {}
    reporting_period = request.GET.get('reporting_period', 'annual')
    
    if filter_form.is_valid():
        applied_filters = {
            filter_form.fields[k].label: v 
            for k, v in filter_form.cleaned_data.items() 
            if v not in (None, '', False)
        }

    # 3. Context - FIX: Use the imported constant REPORTING_PERIOD_CHOICES
    context = {
        'report_title': title,
        'report_type': report_type,
        'report_data': report_data,
        'kpis': kpis,
        'filter_form': filter_form,
        'applied_filters': applied_filters,
        'reporting_period': reporting_period,
        # FIX IS HERE: Use REPORTING_PERIOD_CHOICES directly
        'period_label': dict(REPORTING_PERIOD_CHOICES).get(reporting_period, 'Annual'), 
        'is_income_statement': report_type == 'income_statement', # Flag to show extra columns
    }
    return render(request, 'analysis/analysis_report.html', context)


@login_required
def trend_dashboard_view(request):
    """
    Renders the trend dashboard with time-series data for visualization.
    """
    # 1. Get raw time-series data
    raw_data = generate_mock_analysis_data()
    
    # 2. Extract Labels and Datasets for Charts
    period_labels = []
    chart_datasets = []
    
    if raw_data:
        # Extract X-axis labels (e.g., Q1-2022, Q4-2029) from the first metric
        period_labels = list(raw_data[0]['periods'].keys())
        
        # Prepare datasets for common charts
        for item in raw_data:
            # Scale non-percentage values down to Millions (M) for better chart readability
            scaling_factor = Decimal(1_000_000) if not item['is_percent'] else Decimal(1)
            
            datasets = {
                'label': item['description'],
                'data': [Decimal(v) / scaling_factor for v in item['periods'].values()],
                'is_percent': item['is_percent'],
                'color': f"rgba({random.randint(0, 200)}, {random.randint(0, 200)}, {random.randint(0, 200)}, 0.8)",
            }
            chart_datasets.append(datasets)
            
    # Convert Decimal objects to strings/floats for JSON serialization
    chart_data_json = json.dumps({
        'labels': period_labels,
        'datasets': chart_datasets,
    }, default=str)

    context = {
        'chart_data_json': chart_data_json,
        'report_type': 'Comprehensive Trend Dashboard',
    }
    return render(request, 'analysis/trend_dashboard.html', context)