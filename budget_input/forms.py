# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/budget_input/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Row, Column, HTML
# UPDATED: Import new models and Setup models
from .models import BudgetAssumption, BudgetTransaction, PINDataSubmission
from setup.models import DateDetail, GLAccount, Department, Location, State, Region, RSAFund 

# --- (BudgetAssumptionForm from previous step is retained here) ---

class BudgetAssumptionForm(forms.ModelForm):
    # Override period_start_date to use a ModelChoiceField/Select for validation against DateDetail
    period_start_date = forms.ModelChoiceField(
        queryset=DateDetail.objects.all().order_by('-date'), # Fetch all valid dates
        label="Period Start Date",
        empty_label="--- Select Date ---",
        to_field_name="date", # Use the 'date' field (YYYY-MM-DD) as the value/lookup key
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = BudgetAssumption
        # Exclude metadata fields that will be handled by the view/auto_now_add
        fields = [
            'period_start_date', 'version_name', 'mgmt_fee_rate', 'admin_fee_rate',
            'staff_cost_percent', 'admin_expense_growth', 'new_fund_aum_growth',
            'investment_return_rate', 'target_current_ratio'
        ]
        widgets = {
             'version_name': forms.TextInput(attrs={'placeholder': 'e.g., FY2025 Base Case'}),
        }
        labels = {
            'mgmt_fee_rate': 'Management Fee Rate (e.g., 0.005 for 0.5%)',
            'admin_fee_rate': 'Administrative Fee Rate',
            'staff_cost_percent': 'Staff Cost (% of Revenue)',
            'admin_expense_growth': 'Admin Expense Growth (%)',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Determine if the DateDetail table is empty to show a helpful message
        date_table_empty = not self.fields['period_start_date'].queryset.exists()
        
        date_field_column = Column('period_start_date', css_class='form-group col-md-6 mb-0')
        
        # If the date table is empty, replace the column with an explanatory message
        if date_table_empty:
            date_field_column = Column(
                HTML(f"""
                <div class="alert alert-warning mb-0 p-3">
                    <i class="fas fa-exclamation-triangle me-2"></i> 
                    <strong>Date Table Empty.</strong> Please add dates in 
                    <a href="/setup/datedetail/" class="alert-link">Setup > Date Table</a>.
                </div>
                """), 
                css_class='form-group col-md-6 mb-0'
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                '1. Version & Period',
                Row(
                    Column('version_name', css_class='form-group col-md-6 mb-0'),
                    date_field_column, # Use the dynamic column
                ),
            ),
            Fieldset(
                '2. Revenue Drivers (Percentage of AUM/Balance)',
                Row(
                    Column('mgmt_fee_rate', css_class='form-group col-md-6 mb-0'),
                    Column('admin_fee_rate', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Fieldset(
                '3. Expense & Growth Drivers',
                Row(
                    Column('staff_cost_percent', css_class='form-group col-md-4 mb-0'),
                    Column('admin_expense_growth', css_class='form-group col-md-4 mb-0'),
                    Column('investment_return_rate', css_class='form-group col-md-4 mb-0'),
                ),
            ),
            Fieldset(
                '4. Balance Sheet Targets',
                Row(
                    Column('target_current_ratio', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Submit('submit', 'Save Budget Assumptions', css_class='btn-primary mt-4')
        )


# --- NEW: Budget Transaction Forms (OPEX/CAPEX) ---

class BaseBudgetTransactionForm(forms.ModelForm):
    # Budget Year Choices (Last 5 years + Next 5 years)
    YEAR_CHOICES = [(y, y) for y in range(2023, 2031)]
    budget_year = forms.ChoiceField(choices=YEAR_CHOICES, initial=2026, label="Budget Year")
    
    # To be overridden by subclasses
    transaction_type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = BudgetTransaction
        fields = [
            'budget_year', 'department', 'location', 'gl_account', 'description', 
            'annual_amount', 'justification'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Brief description of the expense/asset'}),
            'annual_amount': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'justification': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Filter GL Accounts to only show postable accounts
        self.fields['gl_account'].queryset = GLAccount.objects.filter(is_postable=True)
        # Add filtering for the location list (optional, showing all for now)
        self.fields['location'].queryset = Location.objects.select_related('state').all()


class OPEXBudgetForm(BaseBudgetTransactionForm):
    class Meta(BaseBudgetTransactionForm.Meta):
        fields = BaseBudgetTransactionForm.Meta.fields + ['category']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'OPEX'
        self.fields['category'].label = "Expense Category"
        self.fields['category'].required = True # Based on PDF structure
        self.fields['annual_amount'].label = "Annual Budget Amount (₦)"
        
        self.helper.layout = Layout(
            Row(
                Column('budget_year', css_class='form-group col-md-4 mb-0'),
                Column('department', css_class='form-group col-md-4 mb-0'),
                Column('location', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('gl_account', css_class='form-group col-md-6 mb-0'),
                Column('category', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('description', css_class='form-group col-md-6 mb-0'),
                Column('annual_amount', css_class='form-group col-md-6 mb-0'),
            ),
            'justification',
            'transaction_type',
            Submit('submit', 'Submit for Approval', css_class='btn-primary mt-4 w-100')
        )


class CAPEXBudgetForm(BaseBudgetTransactionForm):
    class Meta(BaseBudgetTransactionForm.Meta):
        fields = [
            'budget_year', 'department', 'location', 'gl_account', 'description',
            'quantity', 'unit_cost', 'justification'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Asset name/type'}),
            'unit_cost': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'justification': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'unit_cost': 'Unit Cost (₦)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'CAPEX'
        
        self.helper.layout = Layout(
            Row(
                Column('budget_year', css_class='form-group col-md-4 mb-0'),
                Column('department', css_class='form-group col-md-4 mb-0'),
                Column('location', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('gl_account', css_class='form-group col-md-6 mb-0'),
                Column('description', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-0'),
                Column('unit_cost', css_class='form-group col-md-4 mb-0'),
                Column(HTML(
                    '<p class="text-muted small mt-4 pt-2">Total amount calculated as Quantity * Unit Cost.</p>'
                ), css_class='form-group col-md-4 mb-0'),
            ),
            'justification',
            'transaction_type',
            Submit('submit', 'Submit for Approval', css_class='btn-primary mt-4 w-100')
        )


# --- NEW: PIN Data Submission Form ---

class PINDataForm(forms.ModelForm):
    # Budget Year Choices (Last 5 years + Next 5 years)
    YEAR_CHOICES = [(y, y) for y in range(2023, 2031)]
    budget_year = forms.ChoiceField(choices=YEAR_CHOICES, initial=2026, label="Budget Year")
    
    class Meta:
        model = PINDataSubmission
        fields = [
            'budget_year', 'department', 'fund_type', 'active_pins', 
            'non_active_pins', 'never_funded_pins', 'new_enrolments',
            'avg_contribution_existing', 'avg_contribution_new'
        ]
        widgets = {
            'active_pins': forms.NumberInput(attrs={'placeholder': '0'}),
            'non_active_pins': forms.NumberInput(attrs={'placeholder': '0'}),
            'never_funded_pins': forms.NumberInput(attrs={'placeholder': '0'}),
            'new_enrolments': forms.NumberInput(attrs={'placeholder': '0'}),
            'avg_contribution_existing': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'avg_contribution_new': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('budget_year', css_class='form-group col-md-4 mb-0'),
                Column('department', css_class='form-group col-md-4 mb-0'),
                Column('fund_type', css_class='form-group col-md-4 mb-0'),
            ),
            Fieldset(
                'PIN Headcount & Enrolment',
                Row(
                    Column('active_pins', css_class='form-group col-md-3 mb-0'),
                    Column('non_active_pins', css_class='form-group col-md-3 mb-0'),
                    Column('never_funded_pins', css_class='form-group col-md-3 mb-0'),
                    Column('new_enrolments', css_class='form-group col-md-3 mb-0'),
                ),
            ),
            Fieldset(
                'Average Contribution (₦)',
                Row(
                    Column('avg_contribution_existing', css_class='form-group col-md-6 mb-0'),
                    Column('avg_contribution_new', css_class='form-group col-md-6 mb-0'),
                ),
            ),
            Submit('submit', 'Save Entry', css_class='btn-success mt-4 w-100')
        )