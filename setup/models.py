from django.db import models

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
    month = models.PositiveSmallIntegerField(editable=False)
    quarter = models.PositiveSmallIntegerField(editable=False)
    half_year = models.PositiveSmallIntegerField(editable=False)
    year = models.PositiveSmallIntegerField(editable=False)

    def save(self, *args, **kwargs):
        self.month = self.date.month
        self.year = self.date.year
        self.quarter = (self.date.month - 1) // 3 + 1
        self.half_year = 1 if self.date.month <= 6 else 2
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Date Detail"
        verbose_name_plural = "Date Table"
        ordering = ['date']

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} (Q{self.quarter}, H{self.half_year})"
    

# ... (existing imports and other models like RSAFund, State, etc.)

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

# ... (existing other models)


# ... (Existing models: RSAFund, State, Location, Region, ManagedFund, DateDetail, GLAccount)

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