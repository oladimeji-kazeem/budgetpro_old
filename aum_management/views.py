from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AUMCalculationForm
from setup.models import RSAFund, ManagedFund 
from decimal import Decimal
from django.utils.formats import date_format
from django.db.models import Sum
from setup.models import FundTransaction 
from django.template.defaultfilters import register 


# Mock data for growth simulation
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
def aum_dashboard_view(request):
    form = AUMCalculationForm(request.GET or None)
    results = None
    
    if form.is_valid() and form.cleaned_data.get('fund_selection'):
        results = calculate_aum_metrics(form.cleaned_data, MOCK_GROWTH_DATA)

    # AUM KPIs for display (Mocked)
    aum_kpis = [
        {'title': 'Closing AUM', 'value_key': 'closing_aum', 'icon': 'fas fa-chart-line', 'color': 'primary'},
        {'title': 'AUM Growth (%)', 'value_key': 'aum_growth_percent', 'icon': 'fas fa-arrow-up', 'color': 'success'},
        {'title': 'Net Flow (%)', 'value_key': 'net_flow_percent', 'icon': 'fas fa-exchange-alt', 'color': 'info'},
        {'title': 'ROA (%)', 'value_key': 'return_on_asset_percent', 'icon': 'fas fa-percentage', 'color': 'warning'},
    ]
    
    # Mock data for Fund Comparison Table
    comparison_data = [
        {'fund': 'RSA Fund 1', 'aum_latest': 580_000_000, 'yoy_growth': 15.2, 'roa': 8.5},
        {'fund': 'RSA Fund 2', 'aum_latest': 1_250_000_000, 'yoy_growth': 10.1, 'roa': 7.9},
        {'fund': 'CBN RETIREE', 'aum_latest': 2_800_000_000, 'yoy_growth': 22.0, 'roa': 9.1},
        {'fund': 'NNPC', 'aum_latest': 5_100_000_000, 'yoy_growth': 18.5, 'roa': 8.8},
    ]

    context = {
        'form': form,
        'results': results,
        'aum_kpis': aum_kpis,
        'comparison_data': comparison_data,
    }
    return render(request, 'aum_management/aum_dashboard.html', context)