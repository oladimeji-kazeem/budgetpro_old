# predictive_analytics/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Define URLs for the three sub-modules:
# 1. Financial Forecasting
# 2. Performance & Budget Management
# 3. Customer & Operational Insight

@login_required
def analytics_index_view(request):
    """Main hub for Predictive Analytics, linking to sub-modules."""
    sub_modules = [
        {'name': 'Financial Forecasting (AUM, Revenue)', 'url': 'predictive_analytics:financial_forecasting', 'icon': 'fas fa-chart-line', 'color': 'primary'},
        {'name': 'Performance & Budget Management (Risk)', 'url': 'predictive_analytics:budget_management', 'icon': 'fas fa-bullseye', 'color': 'danger'},
        {'name': 'Customer & Operational Insight (PIN Churn)', 'url': 'predictive_analytics:customer_insight', 'icon': 'fas fa-users', 'color': 'success'},
    ]

    context = {
        'sub_modules': sub_modules
    }
    return render(request, 'predictive_analytics/analytics_index.html', context)

@login_required
def financial_forecasting_view(request):
    # Placeholder for AUM/Revenue ML model output
    return render(request, 'predictive_analytics/financial_forecasting.html')

@login_required
def budget_management_view(request):
    # Placeholder for Variance/Rework Prediction ML model output
    return render(request, 'predictive_analytics/budget_management.html')

@login_required
def customer_insight_view(request):
    # Placeholder for PIN Churn/Migration ML model output
    return render(request, 'predictive_analytics/customer_insight.html')