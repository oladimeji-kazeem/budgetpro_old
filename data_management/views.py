from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse 
from .models import UploadHistory
from setup.models import GLTransaction 
from .forms import IncomeStatementFilterForm 
import io 
from openpyxl import Workbook 
from django.utils.formats import number_format 


@login_required
def historical_data_view(request):
    # This view will handle the data import logic (POST request) 
    # and render the UI (GET request).
    
    # 1. Fetch Upload History
    upload_history = UploadHistory.objects.filter(uploaded_by=request.user).order_by('-upload_date')[:10]
    
    # 2. Fetch Sample Recent Transactions (Example: Last 5 transactions)
    recent_transactions = GLTransaction.objects.all().order_by('-created_at')[:5]

    context = {
        'upload_history': upload_history,
        'recent_transactions': recent_transactions,
        # Placeholder for form/logic that handles file upload
        'file_upload_form': None 
    }
    return render(request, 'data_management/historical_data.html', context)


@login_required
def download_excel_template(request, template_type):
    """Generates and serves an Excel file template based on the type requested."""
    
    # Define column headers for different templates
    templates = {
        'gl_transactions': {
            'filename': 'GL_Transactions_Template.xlsx',
            'headers': [
                'transaction_date (YYYY-MM-DD)', 'gl_account_code', 'description', 
                'journal_type', 'document_no', 'reference_no', 'entity_code', 
                'cost_center_code', 'project_code', 'currency_code', 
                'exchange_rate', 'debit', 'credit'
            ]
        },
        'gl_accounts': {
            'filename': 'GL_Chart_of_Accounts_Template.xlsx',
            'headers': [
                'gl_account_code', 'gl_account_name', 'category', 'sub_category',
                'financial_statement (Income Statement/Balance Sheet/Cash Flow)', 
                'account_type (Account/Header)', 'is_postable (TRUE/FALSE)', 
                'parent_account_code', 'normal_balance (Credit/Debit)', 'active_flag (TRUE/FALSE)'
            ]
        },
        'date_table': {
            'filename': 'Date_Detail_Template.xlsx',
            'headers': ['date (YYYY-MM-DD)']
        },
    }

    template_info = templates.get(template_type)

    if not template_info:
        return HttpResponse("Invalid template type requested.", status=404)

    # 1. Create workbook and add headers
    wb = Workbook()
    ws = wb.active
    ws.title = template_info['filename'].replace('.xlsx', '')
    ws.append(template_info['headers'])

    # 2. Prepare in-memory file (BytesIO is essential for Django file serving)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 3. Create HTTP response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={template_info["filename"]}'
    
    return response

@login_required
def income_statement_view(request):
    """Renders the Income Statement page with performance cards and financial data, respecting filters."""
    
    # Initialize form with GET data if filters are applied, otherwise use unbound form
    filter_form = IncomeStatementFilterForm(request.GET)
    
    # Default Period Settings
    period_title = 'FY 2024'
    previous_period_title = 'FY 2023'
    applied_filters = {}
    
    # --- Simulate Filter Application ---
    if filter_form.is_valid():
        # Retrieve filters from the form data
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        
        # Simulate change in report title based on date filter
        if start_date and end_date:
            period_title = f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
            previous_period_title = "Prior Period"
        elif start_date:
            period_title = f"Since {start_date.strftime('%b %d, %Y')}"
            previous_period_title = "Prior Period"
            
        # Collect only non-empty filters for display
        applied_filters = {
            filter_form.fields[k].label: v 
            for k, v in filter_form.cleaned_data.items() 
            if v not in (None, '', False) # Filter out None, empty string, and False
        }

    # Mock Performance Data and Financial Data (Remains static for now)
    performance_cards = [
        {'title': 'Total Revenue', 'value': '₦1.24B', 'change': '+15.2%', 'trend': 'up', 'icon': 'fas fa-arrow-up', 'color': 'success'},
        {'title': 'Operating Expenses', 'value': '₦510M', 'change': '-2.5%', 'trend': 'down', 'icon': 'fas fa-arrow-down', 'color': 'danger'},
        {'title': 'Net Profit', 'value': '₦320M', 'change': '+8.9%', 'trend': 'up', 'icon': 'fas fa-chart-line', 'color': 'primary'},
        {'title': 'Profit Margin', 'value': '25.8%', 'change': '+1.1%', 'trend': 'up', 'icon': 'fas fa-percentage', 'color': 'info'},
    ]
    
    financial_data = [
        {'description': 'REVENUE', 'current': 1240000000, 'previous': 1076000000, 'type': 'header'},
        {'description': 'Management Fees Income', 'current': 950000000, 'previous': 820000000, 'type': 'account'},
        {'description': 'Administrative Fees Income', 'current': 290000000, 'previous': 256000000, 'type': 'account'},
        {'description': 'TOTAL REVENUE', 'current': 1240000000, 'previous': 1076000000, 'type': 'subtotal'},
        
        {'description': 'OPERATING EXPENSES', 'current': 510000000, 'previous': 523000000, 'type': 'header'},
        {'description': 'Staff Costs', 'current': 300000000, 'previous': 310000000, 'type': 'account'},
        {'description': 'Depreciation', 'current': 55000000, 'previous': 52000000, 'type': 'account'},
        {'description': 'Administrative Expenses', 'current': 155000000, 'previous': 161000000, 'type': 'account'},
        {'description': 'TOTAL OPERATING EXPENSES', 'current': 510000000, 'previous': 523000000, 'type': 'subtotal'},
        
        {'description': 'FINANCE INCOME', 'current': 120000000, 'previous': 100000000, 'type': 'header'},
        {'description': 'Interest Income', 'current': 120000000, 'previous': 100000000, 'type': 'account'},
        
        {'description': 'NET PROFIT BEFORE TAX', 'current': 850000000, 'previous': 653000000, 'type': 'major_total'},
    ]
    
    context = {
        'filter_form': filter_form,
        'applied_filters': applied_filters,
        'performance_cards': performance_cards,
        'financial_data': financial_data,
        'period': period_title,
        'previous_period': previous_period_title,
        'report_type': 'Income Statement',
        'period_prefix': 'For the Period Ended:',
    }
    return render(request, 'data_management/income_statement.html', context)


@login_required
def export_income_statement_excel(request):
    """Exports the mock Income Statement data to an Excel file."""
    
    # Replicating the data from income_statement_view
    financial_data = [
        {'description': 'REVENUE', 'current': 1240000000, 'previous': 1076000000, 'type': 'header'},
        {'description': 'Management Fees Income', 'current': 950000000, 'previous': 820000000, 'type': 'account'},
        {'description': 'Administrative Fees Income', 'current': 290000000, 'previous': 256000000, 'type': 'account'},
        {'description': 'TOTAL REVENUE', 'current': 1240000000, 'previous': 1076000000, 'type': 'subtotal'},
        
        {'description': 'OPERATING EXPENSES', 'current': 510000000, 'previous': 523000000, 'type': 'header'},
        {'description': 'Staff Costs', 'current': 300000000, 'previous': 310000000, 'type': 'account'},
        {'description': 'Depreciation', 'current': 55000000, 'previous': 52000000, 'type': 'account'},
        {'description': 'Administrative Expenses', 'current': 155000000, 'previous': 161000000, 'type': 'account'},
        {'description': 'TOTAL OPERATING EXPENSES', 'current': 510000000, 'previous': 523000000, 'type': 'subtotal'},
        
        {'description': 'FINANCE INCOME', 'current': 120000000, 'previous': 100000000, 'type': 'header'},
        {'description': 'Interest Income', 'current': 120000000, 'previous': 100000000, 'type': 'account'},
        
        {'description': 'NET PROFIT BEFORE TAX', 'current': 850000000, 'previous': 653000000, 'type': 'major_total'},
    ]

    wb = Workbook()
    ws = wb.active
    ws.title = "Income Statement FY2024"
    
    # Headers
    ws.append(['Description', 'FY 2024 (Current)', 'FY 2023 (Previous)'])
    
    # Data Rows
    for item in financial_data:
        # Use number_format to ensure Django locale settings (if any) are respected
        current_amount = item['current'] if item['current'] is not None else ''
        previous_amount = item['previous'] if item['previous'] is not None else ''
        
        ws.append([
            item['description'],
            current_amount,
            previous_amount
        ])

    # Prepare in-memory file
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Create HTTP response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Income_Statement_FY2024.xlsx'
    
    return response


@login_required
def balance_sheet_view(request):
    """Renders the Balance Sheet page with performance cards and financial data, respecting filters."""
    
    filter_form = IncomeStatementFilterForm(request.GET)
    
    # Balance Sheet uses an 'As At' period, often the end date
    period_title = 'December 31, 2024'
    previous_period_title = 'December 31, 2023'
    applied_filters = {}
    
    # --- Simulate Filter Application (Only date changes report header) ---
    if filter_form.is_valid():
        end_date = filter_form.cleaned_data.get('end_date')
        if end_date:
            period_title = end_date.strftime('%B %d, %Y')
            previous_period_title = "Prior Year"
        
        applied_filters = {
            filter_form.fields[k].label: v 
            for k, v in filter_form.cleaned_data.items() 
            if v not in (None, '', False)
        }

    # Mock Performance Data
    performance_cards = [
        {'title': 'Total Assets', 'value': '₦2.5B', 'change': '+5.0%', 'trend': 'up', 'icon': 'fas fa-arrow-up', 'color': 'success'},
        {'title': 'Total Liabilities', 'value': '₦1.1B', 'change': '-1.2%', 'trend': 'down', 'icon': 'fas fa-arrow-down', 'color': 'danger'},
        {'title': 'Total Equity', 'value': '₦1.4B', 'change': '+10.5%', 'trend': 'up', 'icon': 'fas fa-chart-line', 'color': 'primary'},
        {'title': 'Current Ratio', 'value': '2.1x', 'change': '-0.1x', 'trend': 'down', 'icon': 'fas fa-percentage', 'color': 'warning'},
    ]
    
    # Mock Balance Sheet Data (Assets = Liabilities + Equity)
    financial_data = [
        {'description': 'ASSETS', 'current': 2500000000, 'previous': 2380000000, 'type': 'section_header'},
        {'description': 'Non-Current Assets', 'current': 1500000000, 'previous': 1400000000, 'type': 'header'},
        {'description': 'Property, Plant & Equipment', 'current': 1450000000, 'previous': 1350000000, 'type': 'account'},
        {'description': 'Current Assets', 'current': 1000000000, 'previous': 980000000, 'type': 'header'},
        {'description': 'Cash & Bank Balances', 'current': 450000000, 'previous': 420000000, 'type': 'account'},
        {'description': 'Trade Receivables', 'current': 550000000, 'previous': 560000000, 'type': 'account'},
        {'description': 'TOTAL ASSETS', 'current': 2500000000, 'previous': 2380000000, 'type': 'major_total'},

        {'description': 'LIABILITIES', 'current': 1100000000, 'previous': 1113000000, 'type': 'section_header'},
        {'description': 'Current Liabilities', 'current': 550000000, 'previous': 560000000, 'type': 'header'},
        {'description': 'Trade Payables', 'current': 300000000, 'previous': 310000000, 'type': 'account'},
        {'description': 'Accrued Liabilities', 'current': 250000000, 'previous': 250000000, 'type': 'account'},
        {'description': 'Non-Current Liabilities', 'current': 550000000, 'previous': 553000000, 'type': 'header'},
        {'description': 'Long-Term Borrowings', 'current': 550000000, 'previous': 553000000, 'type': 'account'},
        {'description': 'TOTAL LIABILITIES', 'current': 1100000000, 'previous': 1113000000, 'type': 'subtotal'},

        {'description': 'EQUITY', 'current': 1400000000, 'previous': 1267000000, 'type': 'section_header'},
        {'description': 'Share Capital', 'current': 800000000, 'previous': 800000000, 'type': 'account'},
        {'description': 'Retained Earnings', 'current': 600000000, 'previous': 467000000, 'type': 'account'},
        {'description': 'TOTAL EQUITY', 'current': 1400000000, 'previous': 1267000000, 'type': 'subtotal'},
        
        {'description': 'TOTAL LIABILITIES & EQUITY', 'current': 2500000000, 'previous': 2380000000, 'type': 'major_total'},
    ]
    
    context = {
        'filter_form': filter_form,
        'applied_filters': applied_filters,
        'performance_cards': performance_cards,
        'financial_data': financial_data,
        'period': period_title,
        'previous_period': previous_period_title,
        'report_type': 'Balance Sheet',
        'period_prefix': 'As At:',
    }
    return render(request, 'data_management/balance_sheet.html', context)


@login_required
def export_balance_sheet_excel(request):
    """Exports the mock Balance Sheet data to an Excel file."""
    
    financial_data = [
        {'description': 'ASSETS', 'current': 2500000000, 'previous': 2380000000, 'type': 'section_header'},
        {'description': 'Non-Current Assets', 'current': 1500000000, 'previous': 1400000000, 'type': 'header'},
        {'description': 'Property, Plant & Equipment', 'current': 1450000000, 'previous': 1350000000, 'type': 'account'},
        {'description': 'Current Assets', 'current': 1000000000, 'previous': 980000000, 'type': 'header'},
        {'description': 'Cash & Bank Balances', 'current': 450000000, 'previous': 420000000, 'type': 'account'},
        {'description': 'Trade Receivables', 'current': 550000000, 'previous': 560000000, 'type': 'account'},
        {'description': 'TOTAL ASSETS', 'current': 2500000000, 'previous': 2380000000, 'type': 'major_total'},

        {'description': 'LIABILITIES', 'current': 1100000000, 'previous': 1113000000, 'type': 'section_header'},
        {'description': 'Current Liabilities', 'current': 550000000, 'previous': 560000000, 'type': 'header'},
        {'description': 'Trade Payables', 'current': 300000000, 'previous': 310000000, 'type': 'account'},
        {'description': 'Accrued Liabilities', 'current': 250000000, 'previous': 250000000, 'type': 'account'},
        {'description': 'Non-Current Liabilities', 'current': 550000000, 'previous': 553000000, 'type': 'header'},
        {'description': 'Long-Term Borrowings', 'current': 550000000, 'previous': 553000000, 'type': 'account'},
        {'description': 'TOTAL LIABILITIES', 'current': 1100000000, 'previous': 1113000000, 'type': 'subtotal'},

        {'description': 'EQUITY', 'current': 1400000000, 'previous': 1267000000, 'type': 'section_header'},
        {'description': 'Share Capital', 'current': 800000000, 'previous': 800000000, 'type': 'account'},
        {'description': 'Retained Earnings', 'current': 600000000, 'previous': 467000000, 'type': 'account'},
        {'description': 'TOTAL EQUITY', 'current': 1400000000, 'previous': 1267000000, 'type': 'subtotal'},
        
        {'description': 'TOTAL LIABILITIES & EQUITY', 'current': 2500000000, 'previous': 2380000000, 'type': 'major_total'},
    ]

    wb = Workbook()
    ws = wb.active
    ws.title = "Balance Sheet"
    
    # Headers
    ws.append(['Description', 'As At 2024 (Current)', 'As At 2023 (Previous)'])
    
    # Data Rows
    for item in financial_data:
        current_amount = item['current'] if item['current'] is not None else ''
        previous_amount = item['previous'] if item['previous'] is not None else ''
        
        ws.append([
            item['description'],
            current_amount,
            previous_amount
        ])

    # Prepare in-memory file
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Create HTTP response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Balance_Sheet_FY2024.xlsx'
    
    return response