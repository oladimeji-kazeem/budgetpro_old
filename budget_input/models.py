# oladimeji-kazeem/budgetpro/budgetpro-ab94e7d262d0d24f247fd60a27eb8be6e83a6e36/budget_input/models.py
from django.db import models
from django.conf import settings
#from setup.models import DateDetail # To link assumptions to a specific period
from setup.models import DateDetail, GLAccount, Location, Region, State, RSAFund, Department
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse


# --- NEW: Approval Status Choices ---
APPROVAL_STATUS_CHOICES = [
    ('PENDING', 'Pending Executive Approval'),
    ('REJECTED', 'Rejected / Requires Rework'),
    ('APPROVED', 'Approved'),
]


class BudgetAssumption(models.Model):
    """
    Stores key editable budget drivers (percentages and values) 
    used to calculate the forward-looking financial statements.
    """
    # Key Fields
    period_start_date = models.ForeignKey(DateDetail, on_delete=models.CASCADE, to_field='date', verbose_name="Period Start Date")
    version_name = models.CharField(max_length=100, unique=True, verbose_name="Budget Version Name")
    
    # Revenue Drivers (Based on typical PFA metrics)
    mgmt_fee_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.005, verbose_name="Mgmt. Fee Rate (%)") # e.g. 0.5%
    admin_fee_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.001, verbose_name="Admin Fee Rate (%)")
    
    # Expense Drivers (Percentage of Revenue/AUM)
    staff_cost_percent = models.DecimalField(max_digits=5, decimal_places=4, default=0.25, verbose_name="Staff Cost (% of Revenue)")
    admin_expense_growth = models.DecimalField(max_digits=5, decimal_places=4, default=0.05, verbose_name="Admin Expense Growth (%)")
    
    # Asset/AUM Growth Drivers (Linked from AUM analysis)
    new_fund_aum_growth = models.DecimalField(max_digits=5, decimal_places=4, default=0.10, verbose_name="New Fund AUM Growth (%)")
    investment_return_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.08, verbose_name="Investment Return Rate (%)")

    # Balance Sheet/Working Capital Drivers
    target_current_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, verbose_name="Target Current Ratio")
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Budget Assumption"
        verbose_name_plural = "Budget Assumptions"
        ordering = ['-period_start_date', 'version_name']

    def __str__(self):
        return f"{self.version_name} ({self.period_start_date.date})"
    
# --- NEW: Budget Transaction (OPEX/CAPEX) Model ---
TRANSACTION_TYPE_CHOICES = [
    ('OPEX', 'Operational Expenditure (OPEX)'),
    ('CAPEX', 'Capital Expenditure (CAPEX)'),
]

class BudgetTransaction(models.Model):
    # Dimensions
    budget_year = models.PositiveSmallIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    
    # Categorization
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    gl_account = models.ForeignKey(GLAccount, on_delete=models.PROTECT, verbose_name="Expense GL Account")
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    
    # OPEX/CAPEX Details
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True) # Used for OPEX Expense Categories
    
    # Financials (Annual Amount in the PDF is distributed monthly/quarterly by the system)
    annual_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Annual Budget Amount (₦)")
    monthly_amount = models.DecimalField(max_digits=18, decimal_places=2, editable=False, verbose_name="Monthly Equivalent (₦)")

    # CAPEX Specific Fields
    quantity = models.IntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Unit Cost (₦)")
    
    justification = models.TextField(blank=True, null=True)
    
    # Workflow Status
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_budgets')
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending Approval') # e.g., Pending Approval, Approved, Rejected
    
    def save(self, *args, **kwargs):
        # Calculate monthly equivalent upon save
        self.monthly_amount = self.annual_amount / 12 if self.annual_amount else 0
        
        # For CAPEX, ensure annual amount matches quantity * unit cost
        if self.transaction_type == 'CAPEX':
             self.annual_amount = self.unit_cost * self.quantity
             
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Budget Transaction"
        verbose_name_plural = "Budget Transactions (OPEX/CAPEX)"
        ordering = ['-budget_year', 'department', 'gl_account']

    def __str__(self):
        return f"{self.transaction_type} {self.budget_year} - {self.department.name} - {self.gl_account.gl_account_code}"


# --- NEW: PIN Data Submission Model ---
class PINDataSubmission(models.Model):
    # Dimensions
    budget_year = models.PositiveSmallIntegerField()
    fund_type = models.ForeignKey(RSAFund, on_delete=models.PROTECT, verbose_name="RSA Fund Type")
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    # PIN Metrics (Historical/Projected)
    active_pins = models.IntegerField(default=0)
    non_active_pins = models.IntegerField(default=0)
    never_funded_pins = models.IntegerField(default=0)
    new_enrolments = models.IntegerField(default=0)
    
    avg_contribution_existing = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Avg Contribution - Existing PINs (₦)")
    avg_contribution_new = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Avg Contribution - New PINs (₦)")
    
# Metadata - UPDATED
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_pin_data')
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pin_data')
    approval_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_pin_data')
    submission_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "PIN Data Submission"
        verbose_name_plural = "PIN Data Submissions"
        unique_together = ('budget_year', 'fund_type', 'department')
        ordering = ['-budget_year', 'department']

    def __str__(self):
        return f"PIN Data {self.budget_year} - {self.department.name} - {self.fund_type.name}"
    
# --- NEW: Approved Budget Version (Snapshot of the approved scenario) ---
class ApprovedBudgetVersion(models.Model):
    version_name = models.CharField(max_length=200, unique=True, verbose_name="Approved Scenario Name")
    forecast_year = models.PositiveSmallIntegerField()
    base_assumption = models.ForeignKey(
        BudgetAssumption, 
        on_delete=models.PROTECT, 
        verbose_name="Base Assumption Used"
    )
    # Key Metrics of the approved forecast
    final_net_profit = models.DecimalField(max_digits=20, decimal_places=2)
    final_closing_cash = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Audit Trail
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_forecasts')
    submission_date = models.DateTimeField(auto_now_add=True)
    
    # Workflow Status
    status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_forecasts')
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Approved Budget Version"
        verbose_name_plural = "Approved Budget Versions"
        ordering = ['-submission_date']

    def __str__(self):
        return f"Approved: {self.version_name} ({self.forecast_year})"

# --- NEW: Forecast GL Transaction (Staging table for approved budget figures) ---
class ForecastGLTransaction(models.Model):
    """
    Stores the final monthly, debit/credit figures derived from an ApprovedBudgetVersion.
    These are the figures that will eventually be used for comparison in the main GL.
    """
    approved_version = models.ForeignKey(ApprovedBudgetVersion, on_delete=models.CASCADE)
    budget_month = models.DateField()
    gl_account = models.ForeignKey(GLAccount, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=2) # Could be Debit (Expense/Asset) or Credit (Revenue/Liability)
    
    class Meta:
        unique_together = ('approved_version', 'budget_month', 'gl_account')
        verbose_name = "Forecast GL Transaction"
        verbose_name_plural = "Forecast GL Transactions"
        ordering = ['budget_month', 'gl_account']

    def __str__(self):
        return f"{self.approved_version.version_name} - {self.budget_month} - {self.gl_account.gl_account_code}"

# --- SIGNAL FOR EMAIL NOTIFICATION ON SUBMISSION ---
@receiver(post_save, sender=ApprovedBudgetVersion)
def send_approval_notification(sender, instance, created, **kwargs):
    if created and instance.status == 'PENDING':
        # Mock Email Sending to an Executive Director
        
        # Build the link to the mock approval dashboard 
        approval_link = f"http://127.0.0.1:8000/budget/approval/{instance.pk}/" 

        subject = f"ACTION REQUIRED: Forecast Budget Submission - {instance.version_name}"
        message = (
            f"A new forecast budget version has been submitted for your approval.\n\n"
            f"Version: {instance.version_name}\n"
            f"Submitted By: {instance.submitted_by.full_name or instance.submitted_by.username}\n"
            f"Net Profit (Forecast): {instance.final_net_profit:,.2f}\n"
            f"Closing Cash (Forecast): {instance.final_closing_cash:,.2f}\n\n"
            f"Please review and approve here: {approval_link}"
        )
        # Mocking the actual email send_mail call:
        print(f"--- MOCK EMAIL SENT --- \nTo: Executive Director\nSubject: {subject}\nBody: {message}")