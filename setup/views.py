from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
# FIX 1: Added Department to model imports
from .models import RSAFund, State, Location, Region, ManagedFund, DateDetail, GLAccount, Department 
# FIX 2: Added DepartmentForm to form imports
from .forms import RSAFundForm, StateForm, LocationForm, RegionForm, ManagedFundForm, DateDetailForm, GLAccountForm, DepartmentForm

# --- Setup Index View ---
@login_required
def setup_index(request):
    """
    Renders the setup index page which links to the CRUD pages.
    """
    setup_models = [
        # ... (Existing models)
        {'name': 'GL Accounts', 'description': 'Manage all General Ledger chart of accounts (COA) records.', 'url_list': reverse('setup:glaccount_list'), 'icon': 'fas fa-book', 'color': '#800080'},
        {'name': 'Departments', 'description': 'Manage internal departments and their heads.', 'url_list': reverse('setup:department_list'), 'icon': 'fas fa-building', 'color': '#ffc107'}, # NEW ENTRY
        {'name': 'RSA Funds', 'description': 'Manage PENCOM RSA Funds.', 'url_list': reverse('setup:rsafund_list'), 'icon': 'fas fa-shield-alt', 'color': '#28a745'},
        {'name': 'States', 'description': 'Manage Nigerian States.', 'url_list': reverse('setup:state_list'), 'icon': 'fas fa-globe-africa', 'color': '#17a2b8'},
        {'name': 'Locations', 'description': 'Manage Locations within States.', 'url_list': reverse('setup:location_list'), 'icon': 'fas fa-map-marker-alt', 'color': '#fd7e14'},
        {'name': 'Regions', 'description': 'Manage Logical Regions.', 'url_list': reverse('setup:region_list'), 'icon': 'fas fa-layer-group', 'color': '#007bff'},
        {'name': 'Managed Funds', 'description': 'Manage Special Managed Funds.', 'url_list': reverse('setup:managedfund_list'), 'icon': 'fas fa-hand-holding-usd', 'color': '#6f42c1'},
        {'name': 'Date Table', 'description': 'Manage Date Details (Month, Quarter, Year).', 'url_list': reverse('setup:date_detail_list'), 'icon': 'fas fa-calendar-alt', 'color': '#e83e8c'},
    ]

    context = {
        'setup_models': setup_models
    }
    return render(request, 'setup/setup_index.html', context)
# --- Base Class for all Setup CRUD Views ---
class BaseSetupView(LoginRequiredMixin):
    # Success URL is determined by the specific model's list view name
    def get_success_url(self):
        model_name = self.model.__name__.lower()
        return reverse_lazy(f'setup:{model_name}_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        context['model_name_singular'] = self.model.__name__.lower()
        return context

# --- RSA Fund CRUD Views ---
class RSAFundListView(BaseSetupView, ListView):
    model = RSAFund
    template_name = 'setup/rsa_fund_list.html'
    context_object_name = 'rsa_funds'

class RSAFundCreateView(BaseSetupView, CreateView):
    model = RSAFund
    form_class = RSAFundForm
    template_name = 'setup/setup_form.html'

class RSAFundUpdateView(BaseSetupView, UpdateView):
    model = RSAFund
    form_class = RSAFundForm
    template_name = 'setup/setup_form.html'

class RSAFundDeleteView(BaseSetupView, DeleteView):
    model = RSAFund
    template_name = 'setup/setup_confirm_delete.html'

# --- State CRUD Views ---
class StateListView(BaseSetupView, ListView):
    model = State
    template_name = 'setup/state_list.html'
    context_object_name = 'states'

class StateCreateView(BaseSetupView, CreateView):
    model = State
    form_class = StateForm
    template_name = 'setup/setup_form.html'

class StateUpdateView(BaseSetupView, UpdateView):
    model = State
    form_class = StateForm
    template_name = 'setup/setup_form.html'

class StateDeleteView(BaseSetupView, DeleteView):
    model = State
    template_name = 'setup/setup_confirm_delete.html'
    
# --- Location CRUD Views (Pattern Repeats) ---
class LocationListView(BaseSetupView, ListView):
    model = Location
    template_name = 'setup/location_list.html'
    context_object_name = 'locations'

class LocationCreateView(BaseSetupView, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'setup/setup_form.html'

class LocationUpdateView(BaseSetupView, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'setup/setup_form.html'

class LocationDeleteView(BaseSetupView, DeleteView):
    model = Location
    template_name = 'setup/setup_confirm_delete.html'

# --- Region CRUD Views (Pattern Repeats) ---
class RegionListView(BaseSetupView, ListView):
    model = Region
    template_name = 'setup/region_list.html'
    context_object_name = 'regions'

class RegionCreateView(BaseSetupView, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'setup/setup_form.html'

class RegionUpdateView(BaseSetupView, UpdateView):
    model = Region
    form_class = RegionForm
    template_name = 'setup/setup_form.html'

class RegionDeleteView(BaseSetupView, DeleteView):
    model = Region
    template_name = 'setup/setup_confirm_delete.html'

# --- ManagedFund CRUD Views (Pattern Repeats) ---
class ManagedFundListView(BaseSetupView, ListView):
    model = ManagedFund
    template_name = 'setup/managed_fund_list.html'
    context_object_name = 'managed_funds'

class ManagedFundCreateView(BaseSetupView, CreateView):
    model = ManagedFund
    form_class = ManagedFundForm
    template_name = 'setup/setup_form.html'

class ManagedFundUpdateView(BaseSetupView, UpdateView):
    model = ManagedFund
    form_class = ManagedFundForm
    template_name = 'setup/setup_form.html'

class ManagedFundDeleteView(BaseSetupView, DeleteView):
    model = ManagedFund
    template_name = 'setup/setup_confirm_delete.html'

# --- NEW: Department CRUD Views ---
class DepartmentListView(BaseSetupView, ListView):
    model = Department
    template_name = 'setup/department_list.html' # New template
    context_object_name = 'departments'

class DepartmentCreateView(BaseSetupView, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'setup/setup_form.html'

class DepartmentUpdateView(BaseSetupView, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'setup/setup_form.html'

class DepartmentDeleteView(BaseSetupView, DeleteView):
    model = Department
    template_name = 'setup/setup_confirm_delete.html'

# --- GL Account CRUD Views ---
class GLAccountListView(BaseSetupView, ListView):
    model = GLAccount
    template_name = 'setup/gl_account_list.html'
    context_object_name = 'gl_accounts'

class GLAccountCreateView(BaseSetupView, CreateView):
    model = GLAccount
    form_class = GLAccountForm
    template_name = 'setup/setup_form.html'

class GLAccountUpdateView(BaseSetupView, UpdateView):
    model = GLAccount
    form_class = GLAccountForm
    template_name = 'setup/setup_form.html'

class GLAccountDeleteView(BaseSetupView, DeleteView):
    model = GLAccount
    template_name = 'setup/setup_confirm_delete.html'

# --- DateDetail CRUD Views (Pattern Repeats) ---
class DateDetailListView(BaseSetupView, ListView):
    model = DateDetail
    template_name = 'setup/date_detail_list.html'
    context_object_name = 'date_details'

class DateDetailCreateView(BaseSetupView, CreateView):
    model = DateDetail
    form_class = DateDetailForm
    template_name = 'setup/setup_form.html'

class DateDetailUpdateView(BaseSetupView, UpdateView):
    model = DateDetail
    form_class = DateDetailForm
    template_name = 'setup/setup_form.html'

class DateDetailDeleteView(BaseSetupView, DeleteView):
    model = DateDetail
    template_name = 'setup/setup_confirm_delete.html'