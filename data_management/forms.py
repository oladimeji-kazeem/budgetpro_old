from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from setup.models import GLTransaction # Import GLTransaction model

REPORTING_PERIOD_CHOICES = [
    ('annual', 'Annual (Yearly)'),
    ('half_yearly', 'Half-Yearly'),
    ('quarterly', 'Quarterly'),
    ('monthly', 'Monthly'),
]

class IncomeStatementFilterForm(forms.Form):
    # Retrieve dynamic choices from GLTransaction table
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get' # Use GET method for filters
        self.helper.form_class = 'bg-white p-4 rounded shadow-sm mb-4'
        self.helper.layout = Layout(
            Row(
                Column('start_date', css_class='form-group col-md-2 mb-0'), # Reduced column size
                Column('end_date', css_class='form-group col-md-2 mb-0'), # Reduced column size
                Column('reporting_period', css_class='form-group col-md-2 mb-0'), # NEW FIELD
                Column('entity', css_class='form-group col-md-2 mb-0'),
                Column('cost_center', css_class='form-group col-md-2 mb-0'),
                Column('journal_type', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('project', css_class='form-group col-md-3 mb-0'),
                Column('currency', css_class='form-group col-md-3 mb-0'),
                Column(
                    Submit('filter', 'Apply Filters', css_class='btn-primary mt-4 w-100'),
                    css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row mt-3'
            )
        )

    # 1. Period Filters
    start_date = forms.DateField(
        required=False,
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label='End Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # NEW PERIOD FIELD
    reporting_period = forms.ChoiceField(
        required=False,
        choices=REPORTING_PERIOD_CHOICES,
        label='Reporting Period',
        initial='annual'
    )

    # Helper function to get distinct choices (must handle cases where GLTransaction is empty)
    def get_choices(field_name, default_label):
        try:
            choices = [(c, c) for c in GLTransaction.objects.values_list(field_name, flat=True).distinct() if c]
        except Exception:
            # Handle error if the GLTransaction table doesn't exist yet or column is missing
            choices = []
        return [('', default_label)] + choices

    entity = forms.ChoiceField(
        required=False,
        choices=get_choices('entity_code', 'All Entities'),
        label='Entity',
    )

    cost_center = forms.ChoiceField(
        required=False,
        choices=get_choices('cost_center_code', 'All Cost Centers'),
        label='Cost Center',
    )

    journal_type = forms.ChoiceField(
        required=False,
        choices=get_choices('journal_type', 'All Journal Types'),
        label='Journal Type',
    )

    project = forms.ChoiceField(
        required=False,
        choices=get_choices('project_code', 'All Projects'),
        label='Project',
    )

    currency = forms.ChoiceField(
        required=False,
        choices=get_choices('currency_code', 'All Currencies'),
        label='Currency',
    )

UPLOAD_TYPE_CHOICES = [
    ('', '--- Select Data Type ---'),
    ('gl_transactions', 'GL Transactions Data'),
    ('gl_accounts', 'GL Accounts (COA)'),
    ('date_table', 'Date Table'),
    ('rsa_fund', 'RSA Fund Historical'),
    ('managed_fund', 'Managed Fund Historical'),
]

class HistoricalDataUploadForm(forms.Form):
    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPE_CHOICES,
        label='Data to Import',
        required=True
    )
    excel_file = forms.FileField(
        label='Select Excel/CSV File',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx,.csv'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'upload_type',
            'excel_file',
            Submit('submit', 'Process & Upload Data', css_class='btn-success w-100 mt-4')
        )