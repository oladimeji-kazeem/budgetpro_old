from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from decimal import Decimal
import datetime # Import for monthly names
# UPDATED: Import DateDetail model
from .forms import BudgetAssumptionForm, OPEXBudgetForm, CAPEXBudgetForm, PINDataForm
from .models import BudgetAssumption, BudgetTransaction, PINDataSubmission
from setup.models import GLAccount, Department, Location, DateDetail # <-- ADDED DateDetail
import json 
from django.db import transaction

@login_required
def submission_index_view(request):
    """
    Renders the main budget submission dashboard with links and recent history.
    """
    context = {
        # Status field changed to PENDING, APPROVED, REJECTED
        'recent_submissions': BudgetTransaction.objects.filter(submitted_by=request.user).order_by('-submission_date')[:5],
        'recent_pin_data': PINDataSubmission.objects.filter(submitted_by=request.user).order_by('-submission_date')[:5],
    }
    return render(request, 'budget_input/submission_index.html', context)


@login_required
def submit_budget_view(request, submission_type):
    """
    Handles OPEX, CAPEX, and PIN Data submissions.
    """
    
    if submission_type == 'opex':
        FormClass = OPEXBudgetForm
        template = 'budget_input/opex_capex_form.html'
        title = "OPEX Budget Submission"
        model_name = "Budget Transaction (OPEX)"
    elif submission_type == 'capex':
        FormClass = CAPEXBudgetForm
        template = 'budget_input/opex_capex_form.html'
        title = "CAPEX Budget Submission"
        model_name = "Budget Transaction (CAPEX)"
    elif submission_type == 'pindata':
        FormClass = PINDataForm
        template = 'budget_input/pindata_form.html'
        title = "PIN Data Submission"
        model_name = "PIN Data Submission"
    else:
        messages.error(request, "Invalid submission type.")
        return redirect('budget_input:submission_index')

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submitted_by = request.user
            
            # Additional logic for CAPEX/OPEX
            if submission_type in ['opex', 'capex']:
                submission.transaction_type = submission_type.upper()
            
            submission.save()
            messages.success(request, f"{model_name} submitted successfully for approval.")
            return redirect('budget_input:submission_index')
        else:
            messages.error(request, "Error submitting form. Please correct the errors below.")
    else:
        form = FormClass()
        
    context = {
        'form': form,
        'title': title,
        'submission_type': submission_type,
    }
    return render(request, template, context)

# --- NEW: Forecast/Statement Generation View ---
@login_required
def generate_forecast_view(request, report_type):
    """
    Generates a tentative Income Statement, Balance Sheet, or Cash Flow 
    based on APPROVED budget submissions and selected assumptions.
    """
    # 1. Determine if all mandatory inputs (assumptions, transactions) are approved
    approved_transactions = BudgetTransaction.objects.filter(status='APPROVED').aggregate(total_annual_opex=Sum('annual_amount', filter=Q(transaction_type='OPEX')), total_annual_capex=Sum('annual_amount', filter=Q(transaction_type='CAPEX')))
    approved_pin_data = PINDataSubmission.objects.filter(status='APPROVED').count()
    active_assumptions = BudgetAssumption.objects.first() # Assume first record is the one in use

    # Safety check for core inputs
    if not active_assumptions or not approved_transactions['total_annual_opex']:
        messages.error(request, "Cannot generate forecast: Missing or unapproved Budget Assumptions/Transactions.")
        return redirect('budget_input:submission_index')
    
    # 2. Mock Data Generation (Simplified placeholder logic)
    if report_type == 'income_statement':
        title = "TENTATIVE INCOME STATEMENT (Forecast)"
        # Revenue = Mock AUM Fee * Fee Rate
        mock_revenue = 100_000_000_000 * float(active_assumptions.mgmt_fee_rate) 
        # Expenses = Approved OPEX + Staff Costs
        total_expenses = approved_transactions['total_annual_opex'] or 0
        total_expenses *= (1 + float(active_assumptions.admin_expense_growth))
        
        financial_data = [
            {'description': 'REVENUE (Forecast)', 'current': mock_revenue, 'type': 'header'},
            {'description': 'TOTAL OPERATING EXPENSES (Approved Budget)', 'current': total_expenses, 'type': 'subtotal'},
            {'description': 'PROFIT BEFORE TAX', 'current': mock_revenue - total_expenses, 'type': 'major_total'},
        ]
    
    elif report_type == 'balance_sheet':
        title = "TENTATIVE BALANCE SHEET (Forecast)"
        financial_data = [
            {'description': 'TOTAL ASSETS (Derived from CAPEX/AUM)', 'current': 5_000_000_000, 'type': 'major_total'},
            {'description': 'TOTAL LIABILITIES & EQUITY (Targeted)', 'current': 5_000_000_000, 'type': 'major_total'},
        ]

    elif report_type == 'cash_flow':
        title = "TENTATIVE CASH FLOW (Forecast)"
        cash_from_ops = (approved_transactions['total_annual_opex'] or 0) * -0.5 
        financial_data = [
            {'description': 'NET CASH FROM OPERATING ACTIVITIES', 'current': cash_from_ops, 'type': 'major_total'},
            {'description': 'NET CASH FROM INVESTING ACTIVITIES', 'current': (approved_transactions['total_annual_capex'] or 0) * -1, 'type': 'major_total'},
        ]
        
    else:
        messages.error(request, "Invalid report type requested.")
        return redirect('budget_input:submission_index')

    context = {
        'title': title,
        'report_type': report_type.replace('_', ' ').title(),
        'financial_data': financial_data, # Use a basic list structure for display
        'period': 'Future Period (Based on Assumptions)',
        'assumptions_version': active_assumptions.version_name if active_assumptions else 'N/A',
        'is_forecast': True,
    }
    return render(request, 'budget_input/forecast_report.html', context)

@login_required
def assumption_dashboard_view(request):
    """
    Renders the main Budget Assumption input/dashboard. (Retained from previous step)
    """
    assumption_pk = request.GET.get('pk')
    current_assumption = None
    
    if assumption_pk:
        # Load existing assumption if pk is provided in the URL
        current_assumption = get_object_or_404(BudgetAssumption, pk=assumption_pk)
        
    if request.method == 'POST':
        form = BudgetAssumptionForm(request.POST, instance=current_assumption)
        if form.is_valid():
            assumption = form.save(commit=False)
            if not assumption.created_by_id:
                assumption.created_by = request.user
            assumption.save()
            messages.success(request, f"Budget assumption '{assumption.version_name}' saved successfully.")
            # Redirect to the saved record's URL to show it loaded
            return redirect(f"{request.path}?pk={assumption.pk}") 
        else:
            messages.error(request, "Error saving assumption. Please check the inputs.")
    else:
        # Load form, either empty or pre-populated with the current_assumption
        form = BudgetAssumptionForm(instance=current_assumption)
        
    # Get all assumptions for the sidebar list
    all_assumptions = BudgetAssumption.objects.all()

    context = {
        'form': form,
        'all_assumptions': all_assumptions,
        'current_assumption': current_assumption, # Pass to template to show what's loaded
    }
    return render(request, 'budget_input/assumption_dashboard.html', context)


@login_required
def forecast_dashboard_view(request):
    """
    Generates the Base Case monthly forecast (IS, BS, CF) for the budget year,
    then presents it in an interactive dashboard for scenario simulation.
    Handles missing setup data by showing blank statements.
    """
    
    # --- 1. Identify Forecast Period and Inputs ---
    latest_date_detail = DateDetail.objects.order_by('-date').first()
    active_assumptions = BudgetAssumption.objects.order_by('-created_at').first()
    
    # Default to blank data if setup is missing (as requested by user)
    forecast_year = datetime.datetime.now().year + 1
    MONTH_NAMES = [datetime.date(2000, m, 1).strftime('%b') for m in range(1, 13)]
    
    forecast_data = {
        'metadata': {
            'year': forecast_year,
            'months': [f'{m}-{str(forecast_year)[2:]}' for m in MONTH_NAMES],
            'version': 'Base Case (No Assumptions)'
        },
        'IS': [],
        'BS': [],
        'CF': []
    }
    
    no_setup_data = not latest_date_detail or not active_assumptions
    
    if no_setup_data:
        if not latest_date_detail:
            messages.warning(request, "Setup incomplete: Date Table is empty. Please add dates in Setup.")
        if not active_assumptions:
            messages.warning(request, "Setup incomplete: No Budget Assumptions found.")
        
        # Keep forecast_data blank (as initialized)
        
    else:
        # --- Continue with calculation only if setup is complete ---
        
        forecast_year = latest_date_detail.year + 1
        
        # --- 2. Fetch Base Inputs (Approved Data and Assumptions) ---
        approved_opex = BudgetTransaction.objects.filter(
            budget_year=forecast_year,
            transaction_type='OPEX',
            status='APPROVED'
        ).aggregate(total=Sum('annual_amount'))['total'] or Decimal(0)
        
        approved_capex = BudgetTransaction.objects.filter(
            budget_year=forecast_year,
            transaction_type='CAPEX',
            status='APPROVED'
        ).aggregate(total=Sum('annual_amount'))['total'] or Decimal(0)
        
        # --- 3. Monthly Forecast Logic (Simplified Base Case) ---
        MONTH_NAMES_LABELS = [f'{m}-{str(forecast_year)[2:]}' for m in MONTH_NAMES]
        
        # Assumptions & Constants
        initial_aum = Decimal(5_000_000_000) 
        
        monthly_opex_base = approved_opex / 12 if approved_opex else Decimal(0)
        monthly_capex_base = approved_capex / 12 if approved_capex else Decimal(0)
        
        # --- Build Financial Statements Data (Base Case for JS) ---
        forecast_data['metadata'] = {
            'year': forecast_year,
            'months': MONTH_NAMES_LABELS,
            'version': active_assumptions.version_name
        }
        
        # Initialize monthly balances for iterative calculation
        aum_monthly = initial_aum
        retained_earnings = Decimal(0)
        cash_balance = Decimal(1_000_000_000)
    
        # --- Line Item Definitions (Mocked) ---
        for month in range(12):
            # I. Income Statement Calculation (Monthly)
            monthly_aum_growth = aum_monthly * active_assumptions.new_fund_aum_growth / 12
            monthly_investment_return = aum_monthly * active_assumptions.investment_return_rate / 12
            
            revenue_mgmt_fee = aum_monthly * active_assumptions.mgmt_fee_rate / 12
            revenue_admin_fee = aum_monthly * active_assumptions.admin_fee_rate / 12
            total_revenue = revenue_mgmt_fee + revenue_admin_fee
            
            staff_costs = total_revenue * active_assumptions.staff_cost_percent
            admin_expenses = monthly_opex_base * (Decimal(1) + active_assumptions.admin_expense_growth / 12)
            total_opex = staff_costs + admin_expenses
            
            pbt = total_revenue + monthly_investment_return - total_opex
            net_profit = pbt * Decimal(0.7) # Mock 30% tax
            tax_amount = pbt * Decimal(0.3)
            
            # II. Balance Sheet Calculation (Cumulative/Ending Balance)
            aum_monthly += monthly_aum_growth
            aum_end_balance = aum_monthly
            retained_earnings += net_profit
            
            # III. Cash Flow Calculation
            net_cash_ops = total_revenue - total_opex 
            net_cash_investing = monthly_capex_base * Decimal(-1)
            net_change_cash = net_cash_ops + net_cash_investing
            opening_cash_prev = cash_balance
            cash_balance += net_change_cash
            
            # --- Store IS Data ---
            forecast_data['IS'].append({
                'period': MONTH_NAMES_LABELS[month],
                'revenue_mgmt_fee': revenue_mgmt_fee,
                'revenue_admin_fee': revenue_admin_fee,
                'total_revenue': total_revenue,
                'staff_costs': staff_costs,
                'admin_expenses': admin_expenses,
                'total_opex': total_opex,
                'investment_return': monthly_investment_return,
                'pbt': pbt,
                'tax': tax_amount,
                'net_profit': net_profit,
            })
            
            # --- Store BS Data (Simplified) ---
            forecast_data['BS'].append({
                'period': MONTH_NAMES_LABELS[month],
                'cash_balance': cash_balance,
                'fixed_assets': monthly_capex_base * (month + 1), # Accumulate CAPEX as assets
                'total_assets': cash_balance + monthly_capex_base * (month + 1) + aum_end_balance,
                'liabilities': Decimal(1_000_000_000), # Fixed initial liabilities
                'retained_earnings': retained_earnings,
                'aum_liability': aum_end_balance, 
                'total_liabilities_equity': Decimal(1_000_000_000) + retained_earnings + aum_end_balance, 
            });
            
            # --- Store CF Data (Simplified) ---
            forecast_data['CF'].append({
                'period': MONTH_NAMES_LABELS[month],
                'net_cash_ops': net_cash_ops,
                'net_cash_investing': net_cash_investing,
                'net_cash_financing': Decimal(0),
                'net_change_cash': net_change_cash,
                'opening_cash': opening_cash_prev,
                'closing_cash': cash_balance,
            });


    context = {
        'forecast_data_json': forecast_data, # Send structured data to JS
        'forecast_year': forecast_year,
        'months': forecast_data['metadata']['months'],
        'assumptions_version': active_assumptions.version_name if active_assumptions else 'N/A',
        'no_setup_data': no_setup_data, # Flag for template
    }
    return render(request, 'budget_input/forecast_dashboard.html', context)

# --- NEW: Forecast Approval Submission View ---
@login_required
@transaction.atomic
def submit_forecast_for_approval_view(request):
    if request.method == 'POST':
        version_name = request.POST.get('version_name')
        final_net_profit = request.POST.get('final_net_profit')
        final_closing_cash = request.POST.get('final_closing_cash')
        full_scenario_data_json = request.POST.get('full_scenario_data')
        
        if not version_name or not final_net_profit or not full_scenario_data_json:
            messages.error(request, "Submission failed: Missing required forecast data.")
            return redirect('budget_input:forecast_dashboard')
            
        try:
            full_scenario_data = json.loads(full_scenario_data_json)
            forecast_year = full_scenario_data['metadata']['year']
            base_assumption = BudgetAssumption.objects.order_by('-created_at').first()
            
            # Check if GL Accounts needed for staging exist (MOCKING)
            revenue_gl = GLAccount.objects.filter(gl_account_code='4000').first() 
            expense_gl = GLAccount.objects.filter(gl_account_code='6000').first()
            if not revenue_gl or not expense_gl:
                 messages.error(request, "Submission failed: Mock GL Accounts (4000 or 6000) not found in setup.")
                 return redirect('budget_input:forecast_dashboard')
            
            # 1. Create the ApprovedBudgetVersion record (Snapshot)
            approved_version = ApprovedBudgetVersion.objects.create(
                version_name=version_name,
                forecast_year=forecast_year,
                base_assumption=base_assumption,
                final_net_profit=Decimal(final_net_profit),
                final_closing_cash=Decimal(final_closing_cash),
                submitted_by=request.user,
                status='PENDING' # Will trigger mock email via signal
            )
            
            # 2. Mock GL Transaction Staging (ForecastGLTransaction)
            for month_data in full_scenario_data['IS']:
                
                # Derive Date (Assuming 1st of the month)
                budget_date_str = f"01-{month_data['period']}"
                budget_date = datetime.datetime.strptime(budget_date_str, "%d-%b-%y").date()

                # Staging: Expense (Debit side)
                ForecastGLTransaction.objects.create(
                    approved_version=approved_version,
                    budget_month=budget_date,
                    gl_account=expense_gl,
                    amount=month_data['total_opex'] * Decimal(-1) # Negative for expense/Debit side
                )
                # Staging: Revenue (Credit side)
                ForecastGLTransaction.objects.create(
                    approved_version=approved_version,
                    budget_month=budget_date,
                    gl_account=revenue_gl,
                    amount=month_data['total_revenue'] # Positive for revenue/Credit side
                )

            messages.success(request, f"Scenario '{version_name}' submitted successfully! Awaiting Executive Director approval. (Mock Email Sent)")
            
        except Exception as e:
            messages.error(request, f"Submission failed due to system error. Make sure GL Accounts 4000 and 6000 exist: {e}")
            return redirect('budget_input:forecast_dashboard') 
        
        return redirect('budget_input:forecast_dashboard')
    
    return redirect('budget_input:forecast_dashboard')