from django.db import models
from django.conf import settings
from django.utils import timezone
import calendar # ADDED for month name calculation


# Define choices based on the GL structure
STATEMENT_CHOICES = [
    ('Income Statement', 'Income Statement'),
    ('Balance Sheet', 'Balance Sheet'),
    ('Cash Flow', 'Cash Flow'),
]

BALANCE_CHOICES = [
    ('Credit', 'Credit'),
    ('Debit', 'Debit'),
]


class RSAFund(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="PENCOM Fund Name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RSA Fund (PENCOM)"
        verbose_name_plural = "RSA Funds (PENCOM)"

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nigerian State")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "State (Nigeria)"
        verbose_name_plural = "States (Nigeria)"

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=150, verbose_name="Location Name")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='locations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'state')
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.name}, {self.state.name}"

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Region Name")
    states = models.ManyToManyField(State, blank=True, related_name='regions')
    locations = models.ManyToManyField(Location, blank=True, related_name='regions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return self.name

class ManagedFund(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Managed Fund Name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Managed Fund"
        verbose_name_plural = "Managed Funds"

    def __str__(self):
        return self.name

class DateDetail(models.Model):
    date = models.DateField(unique=True)
    
    # Fields updated/added per request
    date_key = models.IntegerField(null=True, blank=True, editable=False, db_index=True) # YYYYMMDD
    year = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    quarter = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    month = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    month_name = models.CharField(max_length=10, null=True, blank=True, editable=False, verbose_name="MonthName") # Renamed/set verbose_name to MonthName
    month_short = models.CharField(max_length=3, null=True, blank=True, editable=False)
    day = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True, editable=False) # 1=Monday, 7=Sunday
    day_name = models.CharField(max_length=10, null=True, blank=True, editable=False, verbose_name="DayName") # Renamed/set verbose_name to DayName
    week_of_year = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    is_weekend = models.BooleanField(default=False, editable=False) # Keep default=False
    year_month = models.CharField(max_length=7, null=True, blank=True, editable=False) # YYYY-MM
    year_quarter = models.CharField(max_length=7, null=True, blank=True, editable=False) # YYYY QX
    half_year = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    
    # Fiscal and Calendar Naming - Added fields (1, 2, 3, 4)
    fiscal_year = models.CharField(max_length=10, null=True, blank=True, editable=False) # 1. FYYYYY
    calendar_year = models.CharField(max_length=10, null=True, blank=True, editable=False) # 2. CYYYYY
    quarter_name = models.CharField(max_length=10, null=True, blank=True, editable=False, verbose_name="QtrName") # 3. QX-YYYY (Qtr/Name -> QtrName)
    month_year = models.CharField(max_length=10, null=True, blank=True, editable=False) # 4. MX-YYYY


    def save(self, *args, **kwargs):
        # Calculate fields based on the date
        d = self.date
        
        self.date_key = int(d.strftime('%Y%m%d'))
        self.year = d.year
        self.quarter = (d.month - 1) // 3 + 1
        self.month = d.month
        self.month_name = calendar.month_name[d.month]
        self.month_short = calendar.month_abbr[d.month]
        self.day = d.day
        
        # Python's weekday: Monday is 0 and Sunday is 6. We map to Monday=1, Sunday=7.
        self.day_of_week = d.weekday() + 1 
        self.day_name = calendar.day_name[d.weekday()]
        
        # ISO week number
        self.week_of_year = d.isocalendar()[1]
        
        # Weekend check (Saturday=6, Sunday=7 in our system)
        self.is_weekend = self.day_of_week in [6, 7] 
        
        self.year_month = d.strftime('%Y-%m')
        self.year_quarter = f"{d.year} Q{self.quarter}"
        self.half_year = 1 if d.month <= 6 else 2
        
        # Calculate Fiscal and Calendar Naming (assuming fiscal year = calendar year for simplicity)
        self.fiscal_year = f"FY{d.year}" # 1. FYYYYY
        self.calendar_year = f"CY{d.year}" # 2. CYYYYY
        self.quarter_name = f"Q{self.quarter}-{d.year}" # 3. QX-YYYY (QtrName)
        self.month_year = f"M{d.month}-{d.year}" # 4. MX-YYYY
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Date Detail"
        verbose_name_plural = "Date Table"
        ordering = ['date']

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} ({self.quarter_name})"
    

# Note: The original GLAccount model does not have the table name 'gl_chart_of_accounts',
# but the model name is 'GLAccount', which Django automatically uses for relationship.
from django.db import models
from django.conf import settings
from django.utils import timezone
# --- New GLTransaction Model ---
class GLTransaction(models.Model):
    # transaction_id is automatically provided by Django's primary key (BigAutoField)
    transaction_date = models.DateField(null=False)
    
    # Relationship to GL Account (Foreign Key)
    gl_account_code = models.ForeignKey(
        'GLAccount', 
        to_field='gl_account_code', # Link to the specific code field
        on_delete=models.PROTECT, 
        verbose_name="GL Account Code"
    )
    
    # Relationship to DateDetail (Foreign Key to ensure date consistency)
    date_detail = models.ForeignKey(
        'DateDetail', 
        to_field='date', 
        on_delete=models.PROTECT,
        null=True, # Allow null for transactions that don't match a date in DateDetail
        blank=True,
        verbose_name="Date Details Reference"
    )
    
    description = models.CharField(max_length=255, blank=True, null=True)
    journal_type = models.CharField(max_length=50, blank=True, null=True)
    document_no = models.CharField(max_length=50, blank=True, null=True)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    entity_code = models.CharField(max_length=50, blank=True, null=True)
    cost_center_code = models.CharField(max_length=50, blank=True, null=True)
    project_code = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=10, default='NGN')
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, default=1.000000)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    posted_flag = models.BooleanField(default=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    # Links to the user model specified in settings
    user_posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posted_transactions'
    )
    
    source_module = models.CharField(max_length=50, blank=True, null=True)
    reversal_flag = models.BooleanField(default=False)
    reversal_ref_id = models.BigIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) # Django uses auto_now_add instead of GETDATE()

    class Meta:
        verbose_name = "GL Transaction"
        verbose_name_plural = "GL Transactions"
        # Optional: Add indexes for better performance on common lookups
        indexes = [
            models.Index(fields=['transaction_date', 'gl_account_code']),
        ]

    def __str__(self):
        return f"TRX-{self.pk} ({self.gl_account_code.gl_account_code})"
    

    # --- New FundTransaction Model ---
class FundTransaction(models.Model):
    transaction_date = models.DateField(null=False)
    
    # Links to EITHER ManagedFund OR RSAFund (one must be set, the other null)
    managed_fund = models.ForeignKey(
        'ManagedFund',
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Managed Fund"
    )
    rsa_fund = models.ForeignKey(
        'RSAFund',
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="RSA Fund"
    )
    
    # Common/Derived Financial fields
    entity_code = models.CharField(max_length=50, blank=True, null=True)
    contributions = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    withdrawals = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    # Fields derived from templates but generalized here
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="RSA Fund Balance")
    investment_value = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="Managed Fund Value")
    
    # Source type to distinguish which import created the record
    source_type = models.CharField(max_length=20, choices=[('RSA', 'RSA Fund'), ('MANAGED', 'Managed Fund')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Fund Transaction"
        verbose_name_plural = "Fund Transactions"
        ordering = ['-transaction_date']

    def __str__(self):
        if self.managed_fund:
            return f"Managed Fund TRX ({self.managed_fund.name})"
        elif self.rsa_fund:
            return f"RSA Fund TRX ({self.rsa_fund.name})"
        return f"Fund TRX {self.pk}"
    

# --- New ManagedFundHistorical Model ---
class ManagedFundHistorical(models.Model):
    managed_fund = models.ForeignKey('ManagedFund', on_delete=models.CASCADE)
    period_end_date = models.DateField(db_index=True) # Use this for quarter tracking
    aum_closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    contribution = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    payout = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    expected_asset_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    returns = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_fees = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('managed_fund', 'period_end_date')
        verbose_name = "Managed Fund Historical"
        verbose_name_plural = "Managed Fund Historicals"
        ordering = ['period_end_date']

# --- New RSAFundHistorical Model ---
class RSAFundHistorical(models.Model):
    rsa_fund = models.ForeignKey(RSAFund, on_delete=models.CASCADE)
    period_end_date = models.DateField(db_index=True)
    
    # Financial Metrics
    aum_closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="AUM/Balance")
    average_contribution_existing = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    average_contribution_new = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    
    # Headcount Metrics
    total_pins = models.IntegerField(default=0)
    active_pins = models.IntegerField(default=0)
    never_funded_pins = models.IntegerField(default=0)
    enrolments = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('rsa_fund', 'period_end_date')
        verbose_name = "RSA Fund Historical"
        verbose_name_plural = "RSA Fund Historicals"
        ordering = ['period_end_date']

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Department Name")
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='departments_headed',
        verbose_name="Department Head"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name
        
class GLAccount(models.Model):
    gl_account_code = models.CharField(max_length=15, unique=True, verbose_name="GL Account Code")
    gl_account_name = models.CharField(max_length=200, verbose_name="GL Account Name")
    category = models.CharField(max_length=50, verbose_name="Category")
    sub_category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sub-Category")
    financial_statement = models.CharField(max_length=50, choices=STATEMENT_CHOICES, verbose_name="Financial Statement")
    account_type = models.CharField(max_length=50, verbose_name="Account Type")
    is_postable = models.BooleanField(default=True, verbose_name="Is Postable")
    parent_account = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        limit_choices_to={'is_postable': False}, # Only non-postable (Header) accounts can be parents
        verbose_name="Parent Account"
    )
    normal_balance = models.CharField(max_length=10, choices=BALANCE_CHOICES, verbose_name="Normal Balance")
    active_flag = models.BooleanField(default=True, verbose_name="Active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GL Account"
        verbose_name_plural = "GL Accounts"
        ordering = ['gl_account_code']

    def __str__(self):
        return f"{self.gl_account_code} - {self.gl_account_name}"