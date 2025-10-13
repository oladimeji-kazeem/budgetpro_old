from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, HTML
# FIX: Import TabHolder and Tab from crispy_forms.bootstrap to resolve ImportError
from crispy_forms.bootstrap import TabHolder, Tab
from setup.models import RSAFund, ManagedFund

class AUMCalculationForm(forms.Form):
    # Dynamically pull Fund Choices
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        rsa_funds = RSAFund.objects.all()
        managed_funds = ManagedFund.objects.all()

        FUND_CHOICES = [
            ('', '--- Select Fund ---'),
            ('RSA', '--- RSA Funds (Requires RSA Inputs) ---'),
        ] + [(f'RSA_{f.id}', f.name) for f in rsa_funds] + [
            ('MANAGED', '--- Managed Funds (Requires Managed Inputs) ---'),
        ] + [(f'MAN_{f.id}', f.name) for f in managed_funds]
        
        self.fields['fund_selection'].choices = FUND_CHOICES
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'bg-white p-4 rounded shadow-lg'
        self.helper.layout = Layout(
            # --- Tabbed Input Sections ---
            TabHolder(
                Tab(
                    '1. Fund & Period Selection',
                    Row(
                        Column('fund_selection', css_class='form-group col-md-6 mb-0'),
                        Column('start_date', css_class='form-group col-md-3 mb-0'),
                        Column('end_date', css_class='form-group col-md-3 mb-0'),
                        css_class='form-row'
                    ),
                    HTML('<p class="text-muted small mt-4">Note: Detail inputs for Managed/RSA Funds are on the corresponding tabs.</p>')
                ),
                
                Tab(
                    '2. Managed Fund Drivers',
                    HTML('<p class="text-muted small mb-4">Inputs for Managed Fund projections.</p>'),
                    Row(
                        Column('fund_launch_date', css_class='form-group col-md-6 mb-0'),
                        Column('fund_start_amount', css_class='form-group col-md-6 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('quarterly_growth_rate', css_class='form-group col-md-6 mb-0'),
                        Column('quarterly_return_rate', css_class='form-group col-md-6 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('fee_structure', css_class='form-group col-md-6 mb-0'),
                        Column('referral_agency_cost_rate', css_class='form-group col-md-6 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('operating_expense_percent', css_class='form-group col-md-6 mb-0'),
                        Column('agency_referral_cost', css_class='form-group col-md-6 mb-0'),
                        css_class='form-row'
                    )
                ),

                Tab(
                    '3. RSA Fund Drivers',
                    HTML('<p class="text-muted small mb-4">Inputs for RSA PINS, Contributions, and Fees.</p>'),
                    Row(
                        Column('enrolment_growth_rate', css_class='form-group col-md-4 mb-0'),
                        Column('avg_contribution_growth_rate', css_class='form-group col-md-4 mb-0'),
                        Column('payout_ratio', css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('total_pins', css_class='form-group col-md-3 mb-0'),
                        Column('active_pins', css_class='form-group col-md-3 mb-0'),
                        Column('non_active_pins', css_class='form-group col-md-3 mb-0'),
                        Column('never_funded_pins', css_class='form-group col-md-3 mb-0'),
                        css_class='form-row mt-3'
                    ),
                    Row(
                        Column('admin_fee_rate', css_class='form-group col-md-3 mb-0'),
                        Column('pfa_fee_rate', css_class='form-group col-md-3 mb-0'),
                        Column('pfc_fee_rate', css_class='form-group col-md-3 mb-0'),
                        Column('pencom_fee_rate', css_class='form-group col-md-3 mb-0'),
                        css_class='form-row mt-3'
                    )
                ),
                css_class='mb-4'
            ),

            # --- AUM Computation Approach (Core Formula: Visible Below Tabs) ---
            Fieldset(
                '4. Core AUM Computation (Final Formula)',
                HTML('<p class="text-muted small">Formula: Opening AUM + Contributions - Payouts + Investment Return - Total Fees = Closing AUM</p>'),
                Row(
                    Column('opening_aum', css_class='form-group col-md-3 mb-0'),
                    Column('contributions', css_class='form-group col-md-3 mb-0'),
                    Column('payouts', css_class='form-group col-md-3 mb-0'),
                    Column('investment_return', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('total_fees', css_class='form-group col-md-6 mb-0'),
                    Column(
                        Submit('calculate', 'Calculate AUM & Growth', css_class='btn-primary w-100 mt-4'),
                        css_class='form-group col-md-6 mb-0'
                    ),
                    css_class='form-row mt-3'
                ),
            ),
        )

    # Core Selection Fields
    fund_selection = forms.ChoiceField(label='Fund to Analyze', required=True)
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Core Formula Fields
    opening_aum = forms.DecimalField(label='Opening AUM (₦)', required=False, initial=0)
    contributions = forms.DecimalField(label='+ Contributions (₦)', required=False, initial=0)
    payouts = forms.DecimalField(label='- Payouts (₦)', required=False, initial=0)
    investment_return = forms.DecimalField(label='+ Investment Return (₦)', required=False, initial=0)
    total_fees = forms.DecimalField(label='- Total Fees (₦)', required=False, initial=0)

    # Managed Fund Drivers
    fund_launch_date = forms.DateField(label='Fund Launch Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fund_start_amount = forms.DecimalField(label='Fund Start Amount (₦)', required=False, initial=0)
    quarterly_growth_rate = forms.DecimalField(label='Quarterly Growth Rate (%)', required=False, initial=0.0)
    quarterly_return_rate = forms.DecimalField(label='Quarterly Return Rate (%)', required=False, initial=0.0)
    fee_structure = forms.CharField(label='Fee Structure', required=False)
    referral_agency_cost_rate = forms.DecimalField(label='Referral/Agency Cost Rate (%)', required=False, initial=0.0)
    operating_expense_percent = forms.DecimalField(label='Operating Expense %', required=False, initial=0.0)
    agency_referral_cost = forms.DecimalField(label='Agency/Referral Cost (₦)', required=False, initial=0) 

    # RSA Drivers
    enrolment_growth_rate = forms.DecimalField(label='Enrolment Growth Rate (%)', required=False, initial=0.0)
    avg_contribution_growth_rate = forms.DecimalField(label='Avg Contrib. Growth Rate (%)', required=False, initial=0.0)
    payout_ratio = forms.DecimalField(label='Payout Ratio (% of Contributions)', required=False, initial=0.0)
    total_pins = forms.IntegerField(label='Total PINs', required=False, initial=0)
    active_pins = forms.IntegerField(label='Active PINs', required=False, initial=0)
    non_active_pins = forms.IntegerField(label='Non-Active PINs', required=False, initial=0)
    never_funded_pins = forms.IntegerField(label='Never-Funded PINs', required=False, initial=0)
    admin_fee_rate = forms.DecimalField(label='Admin Fee Rate (%)', required=False, initial=0.0)
    pfa_fee_rate = forms.DecimalField(label='PFA Fee Rate (%)', required=False, initial=0.0)
    pfc_fee_rate = forms.DecimalField(label='PFC Fee Rate (%)', required=False, initial=0.0)
    pencom_fee_rate = forms.DecimalField(label='PENCOM Fee Rate (%)', required=False, initial=0.0)