# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/aum_management/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, HTML, Div
from crispy_forms.bootstrap import TabHolder, Tab
from setup.models import RSAFund, ManagedFund
from decimal import Decimal

# --- 1. AUM CALCULATION FORM (Simplified to match screenshot 1) ---
class AUMCalculationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        rsa_funds = RSAFund.objects.all()
        managed_funds = ManagedFund.objects.all()

        FUND_CHOICES = [
            ('', '--- Select Fund ---'),
        ] + [(f'RSA_{f.id}', f.name) for f in rsa_funds] + [
            ('MANAGED', '--- Managed Funds ---'),
        ] + [(f'MAN_{f.id}', f.name) for f in managed_funds]
        
        self.fields['fund_selection'].choices = FUND_CHOICES
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'p-4 rounded shadow-lg'
        self.helper.layout = Layout(
            Fieldset(
                'AUM Calculation & Tracking',
                Row(
                    Column('fund_selection', css_class='form-group col-md-6 mb-0'),
                    Column('is_existing_fund', css_class='form-group col-md-6 mb-0 pt-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('opening_aum', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Growth & Fee Assumptions',
                Row(
                    Column('contribution_growth_rate', css_class='form-group col-md-6 mb-0'),
                    Column('rate_of_return', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('pfa_fee_rate', css_class='form-group col-md-4 mb-0'),
                    Column('admin_fee_rate', css_class='form-group col-md-4 mb-0'),
                    Column(
                        Submit('calculate', 'Calculate & Save AUM', css_class='btn-primary w-100 mt-0'),
                        css_class='form-group col-md-4 mb-0 pt-4'
                    ),
                    css_class='form-row'
                ),
                # Hidden core fields for passing data to view logic
                Div('contributions', 'payouts', 'investment_return', 'total_fees', css_class='d-none'),
            )
        )

    fund_selection = forms.ChoiceField(label='Fund Type', required=True)
    is_existing_fund = forms.BooleanField(label='Is this an Existing Fund?', required=False, initial=True)
    opening_aum = forms.DecimalField(label='Opening AUM (₦)', required=False, initial=Decimal(0), widget=forms.NumberInput(attrs={'placeholder': '100'}))
    contribution_growth_rate = forms.DecimalField(label='Contribution Growth (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0.0'}))
    rate_of_return = forms.DecimalField(label='Rate of Return (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0.0'}))
    pfa_fee_rate = forms.DecimalField(label='PFA Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    admin_fee_rate = forms.DecimalField(label='Admin Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    contributions = forms.DecimalField(required=False, initial=Decimal(0))
    payouts = forms.DecimalField(required=False, initial=Decimal(0))
    investment_return = forms.DecimalField(required=False, initial=Decimal(0))
    total_fees = forms.DecimalField(required=False, initial=Decimal(0))
    

# --- 2. AUM DRIVER FORM (Matches screenshot 1, middle section) ---
class AUMDriverForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        rsa_funds = RSAFund.objects.all()
        managed_funds = ManagedFund.objects.all()

        FUND_CHOICES = [
            ('', '--- Select Fund ---'),
        ] + [(f'RSA_{f.id}', f.name) for f in rsa_funds] + [(f'MAN_{f.id}', f.name) for f in managed_funds]
        
        YEAR_CHOICES = [('', 'Select Year')] + [(str(y), str(y)) for y in range(2023, 2028)]
        QUARTER_CHOICES = [('', 'Select Quarter'), ('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')]
        
        self.fields['fund_type'].choices = FUND_CHOICES
        self.fields['year'].choices = YEAR_CHOICES
        self.fields['quarter'].choices = QUARTER_CHOICES
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'p-4 rounded shadow-lg'
        self.helper.layout = Layout(
            Row(
                Column('fund_type', css_class='form-group col-md-6 mb-0'),
                Column('calculation_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('year', css_class='form-group col-md-6 mb-0'),
                Column('quarter', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Fieldset(
                'Growth & Return Drivers',
                Row(
                    Column('initial_contribution', css_class='form-group col-md-6 mb-0'),
                    Column('payout_growth_rate', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('contribution_growth_rate', css_class='form-group col-md-6 mb-0'),
                    Column('rate_of_return', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            
            Fieldset(
                'Fee Structure Drivers',
                Row(
                    Column('pfa_fee_rate', css_class='form-group col-md-3 mb-0'),
                    Column('admin_fee_rate', css_class='form-group col-md-3 mb-0'),
                    Column('pfc_fee_rate', css_class='form-group col-md-3 mb-0'),
                    Column('pencom_fee_rate', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('vat_fee_rate', css_class='form-group col-md-4 mb-0'),
                    Column(
                        Submit('save_drivers', 'Save AUM Drivers', css_class='btn-primary w-100 mt-0'),
                        css_class='form-group col-md-8 mb-0 pt-4'
                    ),
                    css_class='form-row'
                ),
            )
        )
    
    fund_type = forms.ChoiceField(label='Fund Type', required=True)
    calculation_date = forms.DateField(label='Calculation Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    year = forms.ChoiceField(label='Year', required=False)
    quarter = forms.ChoiceField(label='Quarter', required=False)
    initial_contribution = forms.DecimalField(label='Initial Contribution (₦)', required=False, initial=Decimal(0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    contribution_growth_rate = forms.DecimalField(label='Contribution Growth (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    payout_growth_rate = forms.DecimalField(label='Payout Growth (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    rate_of_return = forms.DecimalField(label='Rate of Return (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    pfa_fee_rate = forms.DecimalField(label='PFA Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    admin_fee_rate = forms.DecimalField(label='Admin Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    pfc_fee_rate = forms.DecimalField(label='PFC Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    pencom_fee_rate = forms.DecimalField(label='PENCOM Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))
    vat_fee_rate = forms.DecimalField(label='VAT Fee (%)', required=False, initial=Decimal(0.0), widget=forms.NumberInput(attrs={'placeholder': '0'}))


# --- 3. RSA HISTORICAL FORM (Matches screenshot 2, top section) ---
class RSAHistoricalForm(forms.Form):
    def __init__(self, rsa_funds, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rsa_funds = rsa_funds
        
        # Add dynamic fields for AUM Closing Balance
        for fund in rsa_funds:
            self.fields[f'rsa_fund_{fund.id}'] = forms.DecimalField(
                label=fund.name,
                required=False,
                initial=Decimal(0.00),
                widget=forms.NumberInput(attrs={'placeholder': '0.00'})
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'p-4 rounded shadow-lg'
        
        fund_columns = []
        for fund in rsa_funds:
            fund_columns.append(Column(f'rsa_fund_{fund.id}', css_class='form-group col-md-4 mb-0'))
        
        while len(fund_columns) % 3 != 0:
            fund_columns.append(Column(css_class='form-group col-md-4 mb-0'))
            
        fund_rows = [Row(*fund_columns[i:i+3], css_class='form-row mt-3') for i in range(0, len(fund_columns), 3)]
        
        self.helper.layout = Layout(
            Row(
                Column('period_date', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Fieldset(
                'RSA Fund Values',
                *fund_rows
            ),
            Submit('save_rsa_historical', 'Save RSA Historical Data', css_class='btn-primary w-100 mt-4')
        )

    period_date = forms.DateField(label='Period Date', required=True, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'dd/mm/yyyy'}))


# --- 4. MANAGED FUND HISTORICAL FORM (Matches screenshot 2, bottom section) ---
class ManagedFundHistoricalForm(forms.Form):
    
    # Components from screenshot 2, bottom section
    COMPONENT_FIELDS = [
        'Gainers', 'CBN Balance', 'FBN', 'TCF', 'NNPC', 'Dangote', 'Comet', 
        'PIMMA', 'CHEVRON, MTN or NDA', 'CBN', 'Figma', 'OMS', 
        'Niger Delta', 'A of P Foods', 'St Saviors', 'Leadway. Ass', 'LaLao', 'PNG GAS'
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        managed_funds = ManagedFund.objects.all()
        FUND_CHOICES = [('', 'Select Fund Name')] + [(f.id, f.name) for f in managed_funds]
        self.fields['fund_name'].choices = FUND_CHOICES
        
        for component in self.COMPONENT_FIELDS:
            field_name = component.lower().replace('.', '').replace(',', '').replace(' ', '_').replace('or', '_')
            self.fields[field_name] = forms.DecimalField(
                label=component,
                required=False,
                initial=Decimal(0.00),
                widget=forms.NumberInput(attrs={'placeholder': '0.00'})
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'p-4 rounded shadow-lg'
        
        component_columns = []
        for component in self.COMPONENT_FIELDS:
            field_name = component.lower().replace('.', '').replace(',', '').replace(' ', '_').replace('or', '_')
            component_columns.append(Column(field_name, css_class='form-group col-md-4 mb-0'))

        while len(component_columns) % 3 != 0:
            component_columns.append(Column(css_class='form-group col-md-4 mb-0'))
            
        component_rows = [Row(*component_columns[i:i+3], css_class='form-row mt-3') for i in range(0, len(component_columns), 3)]
        
        self.helper.layout = Layout(
            Row(
                Column('period_date', css_class='form-group col-md-6 mb-0'),
                Column('fund_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('aum_closing_balance', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Fieldset(
                'Fund Components',
                *component_rows
            ),
            Submit('save_managed_historical', 'Save Managed Fund Data', css_class='btn-primary w-100 mt-4')
        )

    period_date = forms.DateField(label='Period Date', required=True, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'dd/mm/yyyy'}))
    fund_name = forms.ChoiceField(label='Fund Name', required=True)
    aum_closing_balance = forms.DecimalField(label='AUM Closing Balance', required=False, initial=Decimal(0.00), widget=forms.NumberInput(attrs={'placeholder': '0.00'}))