# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/aum_management/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AUMCalculationForm, AUMDriverForm, RSAHistoricalForm, ManagedFundHistoricalForm
# UPDATED: Import the historical models
from setup.models import RSAFund, ManagedFund, RSAFundHistorical, ManagedFundHistorical 
from decimal import Decimal
from django.utils.formats import date_format
from django.db.models import Sum
from setup.models import FundTransaction 
from django.template.defaultfilters import register 


# Mock data for growth simulation (retained)
MOCK_GROWTH_DATA = {
    'RSA_1': {'initial_aum': 500_000_000, 'net_contributions': 50_000_000, 'payouts': 10_000_000, 'net_returns': 10_000_000, 'total_fees': 2_000_000},
    'MAN_1': {'initial_aum': 1_200_000_000, 'net_contributions': 75_000_000, 'payouts': 15_000_000, 'net_returns': 15_000_000, 'total_fees': 3_000_000},
}

def calculate_aum_metrics(form_data, growth_data):
    """
    Calculates AUM metrics using the PFA AUM Growth Model approach.
    Formula: Closing AUM = Opening AUM + Contributions - Payouts + Investment Return - Total Fees.
    """
    
    fund_selection = form_data.get('fund_selection', '')
    
    # --- FIX: Corrected typo from fund_fund_selection to fund_selection ---
    if not fund_selection or fund_selection in ['RSA', 'MANAGED']:
        return None
        
    # Example: fund_selection = 'RSA_1' -> fund_type='RSA', fund_id_str='1'
    fund_type, fund_id_str = fund_selection.split('_')
    
    try:
        fund_id = int(fund_id_str)
    except ValueError:
        # Handles malformed data if the ID part is not an integer
        return None

    # Get Fund Name safely
    if fund_type == 'RSA':
        fund_obj = RSAFund.objects.filter(id=fund_id).first()
        fund_key = f"RSA_{fund_id}"
    elif fund_type == 'MAN':
        fund_obj = ManagedFund.objects.filter(id=fund_id).first()
        fund_key = f"MAN_{fund_id}"
    else:
        return None
        
    if not fund_obj:
         return None 
    
    fund_name = fund_obj.name

    # --- PFA AUM Calculation Components (Overridden by Manual Inputs) ---
    # These map directly to the AUM Computation Approach drivers.
    initial_aum = Decimal(form_data.get('opening_aum', growth_data.get(fund_key, {}).get('initial_aum', 500_000_000)))
    contributions = Decimal(form_data.get('contributions', growth_data.get(fund_key, {}).get('net_contributions', 50_000_000)))
    payouts = Decimal(form_data.get('payouts', growth_data.get(fund_key, {}).get('payouts', 10_000_000)))
    investment_return = Decimal(form_data.get('investment_return', growth_data.get(fund_key, {}).get('net_returns', 10_000_000)))
    total_fees = Decimal(form_data.get('total_fees', growth_data.get(fund_key, {}).get('total_fees', 2_000_000)))
    
    # Core Calculation: Closing AUM = Opening AUM + Contributions - Payouts + Investment Return - Total Fees
    closing_aum = initial_aum + contributions - payouts + investment_return - total_fees
    
    # --- KPIs/Metrics ---
    
    aum_growth = closing_aum - initial_aum
    aum_growth_percent = (aum_growth / initial_aum) * 100 if initial_aum else Decimal(0)
    net_flow = contributions - payouts
    net_flow_percent = (net_flow / initial_aum) * 100 if initial_aum else Decimal(0)
    return_on_asset_percent = (investment_return / initial_aum) * 100 if initial_aum else Decimal(0)
    
    return {
        'fund_name': fund_name,
        'initial_aum': initial_aum,
        'contributions': contributions,
        'payouts': payouts,
        'investment_return': investment_return,
        'total_fees': total_fees,
        'closing_aum': closing_aum,
        'aum_growth': aum_growth,
        'aum_growth_percent': aum_growth_percent,
        'net_flow': net_flow,
        'net_flow_percent': net_flow_percent,
        'return_on_asset_percent': return_on_asset_percent,
        'start_date': form_data.get('start_date'),
        'end_date': form_data.get('end_date'),
    }


@login_required
def aum_calculation_view(request):
    """Handles the main AUM Calculation tab (replaces aum_dashboard_view)."""
    form = AUMCalculationForm(request.GET or None)
    results = None
    
    if form.is_valid() and form.cleaned_data.get('fund_selection'):
        # NOTE: The logic below is simplified since the new form hides most inputs.
        # In a real scenario, these would be retrieved from AUMDriver models.
        results = calculate_aum_metrics(form.cleaned_data, MOCK_GROWTH_DATA)

    aum_kpis = [
        {'title': 'Closing AUM', 'value_key': 'closing_aum', 'icon': 'fas fa-chart-line', 'color': 'primary'},
        {'title': 'AUM Growth (%)', 'value_key': 'aum_growth_percent', 'icon': 'fas fa-arrow-up', 'color': 'success'},
        {'title': 'Net Flow (%)', 'value_key': 'net_flow_percent', 'icon': 'fas fa-exchange-alt', 'color': 'info'},
        {'title': 'ROA (%)', 'value_key': 'return_on_asset_percent', 'icon': 'fas fa-percentage', 'color': 'warning'},
    ]
    
    # Fetch real fund names and use mock data for metrics
    comparison_data = [
        {'fund': fund.name, 'aum_latest': Decimal(580_000_000) + i*10_000_000, 'yoy_growth': 15.2 + i, 'roa': 8.5 + i*0.1} 
        for i, fund in enumerate(list(RSAFund.objects.all()[:2]) + list(ManagedFund.objects.all()[:2]))
    ]
    # Ensure at least mock data is available if no funds are in DB
    if not comparison_data:
        comparison_data = [
            {'fund': 'RSA Fund 1', 'aum_latest': 580_000_000, 'yoy_growth': 15.2, 'roa': 8.5},
            {'fund': 'CBN RETIREE', 'aum_latest': 2_800_000_000, 'yoy_growth': 22.0, 'roa': 9.1},
        ]


    context = {
        'form': form,
        'results': results,
        'aum_kpis': aum_kpis,
        'comparison_data': comparison_data,
        'active_tab': 'aum_calculation', # Set active tab
    }
    return render(request, 'aum_management/aum_dashboard.html', context)


@login_required
def aum_drivers_view(request):
    """Handles the AUM Drivers (Assumptions) tab."""
    # Since AUMDriver model doesn't exist, we mock data based on existing funds
    # A real implementation would query AUMDriver.objects.all()
    
    if request.method == 'POST':
        form = AUMDriverForm(request.POST)
        if form.is_valid():
            # Mock success and initial data persistence
            context = {
                'form': AUMDriverForm(initial=form.cleaned_data),
                'message': f"AUM Drivers for {dict(form.fields['fund_type'].choices).get(form.cleaned_data.get('fund_type'))} saved successfully.",
                'active_tab': 'aum_drivers',
            }
            return render(request, 'aum_management/aum_drivers.html', context)
    else:
        form = AUMDriverForm()
    
    # Mock retrieval of saved data from DB based on existing Funds
    mock_saved_drivers = [
        {'fund_name': f.name, 'year_quarter': '2024 / Q4', 'contribution_growth': '5.0%', 'return_rate': '7.5%', 'pfa_fee': '0.02%', 'date': '2024-12-31'}
        for f in ManagedFund.objects.all()[:5]
    ]
    
    context = {
        'form': form,
        'mock_saved_drivers': mock_saved_drivers,
        'active_tab': 'aum_drivers',
    }
    return render(request, 'aum_management/aum_drivers.html', context)


@login_required
def rsa_historical_view(request):
    """Handles the RSA Fund Historical Data tab."""
    rsa_funds = RSAFund.objects.filter(is_active=True).order_by('id')
    
    if request.method == 'POST':
        form = RSAHistoricalForm(rsa_funds, request.POST)
        if form.is_valid():
            # TODO: Add logic to save RSAFundHistorical instances here
            # Mock success and clear form
            context = {
                'form': RSAHistoricalForm(rsa_funds),
                'rsa_funds': rsa_funds,
                'message': 'RSA Historical Data saved successfully.',
                'active_tab': 'rsa_historical',
            }
            return render(request, 'aum_management/rsa_historical.html', context)
    else:
        form = RSAHistoricalForm(rsa_funds)
    
    # Fetch data from the database
    # Orders by date descending and fund name to get recent history grouped by fund
    recent_rsa_history = RSAFundHistorical.objects.select_related('rsa_fund').order_by('-period_end_date', 'rsa_fund__name')[:10]
        
    context = {
        'form': form,
        'rsa_funds': rsa_funds,
        'recent_rsa_history': recent_rsa_history, # Passed data from database
        'active_tab': 'rsa_historical',
    }
    return render(request, 'aum_management/rsa_historical.html', context)


@login_required
def managed_fund_historical_view(request):
    """Handles the Managed Fund Historical Data tab."""
    managed_funds = ManagedFund.objects.all().order_by('id')
    
    if request.method == 'POST':
        form = ManagedFundHistoricalForm(request.POST)
        if form.is_valid():
            # TODO: Add logic to save ManagedFundHistorical instances here
            # Mock success and clear form
            context = {
                'form': ManagedFundHistoricalForm(),
                'managed_funds': managed_funds,
                'message': 'Managed Fund Historical Data saved successfully.',
                'active_tab': 'managed_fund_historical',
            }
            return render(request, 'aum_management/managed_fund_historical.html', context)
    else:
        form = ManagedFundHistoricalForm()

    # Fetch data from the database
    recent_managed_history = ManagedFundHistorical.objects.select_related('managed_fund').order_by('-period_end_date', 'managed_fund__name')[:10]

    context = {
        'form': form,
        'managed_funds': managed_funds,
        'recent_managed_history': recent_managed_history, # Passed data from database
        'active_tab': 'managed_fund_historical',
    }
    return render(request, 'aum_management/managed_fund_historical.html', context)