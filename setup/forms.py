from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import RSAFund, State, Location, Region, ManagedFund, DateDetail

class BaseSetupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            *self.fields.keys(),
            Submit('submit', 'Save Record', css_class='btn-primary mt-3')
        )
        self.helper.form_method = 'post'

# 1. RSAFund Forms
class RSAFundForm(BaseSetupForm):
    class Meta:
        model = RSAFund
        fields = ('name', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Fund II'}),
        }

# 2. State Forms
class StateForm(BaseSetupForm):
    class Meta:
        model = State
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Lagos'}),
        }

# 3. Location Forms
class LocationForm(BaseSetupForm):
    class Meta:
        model = Location
        fields = ('name', 'state')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Ikeja'}),
        }

# 4. Region Forms
class RegionForm(BaseSetupForm):
    class Meta:
        model = Region
        fields = ('name', 'states', 'locations')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., South West'}),
        }

# 5. ManagedFund Forms
class ManagedFundForm(BaseSetupForm):
    class Meta:
        model = ManagedFund
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., GUINNESS'}),
        }

# 6. DateDetail Forms
class DateDetailForm(BaseSetupForm):
    class Meta:
        model = DateDetail
        fields = ('date',)
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom helper layout for DateDetail (optional, just to show how to customize)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'date',
            Submit('submit', 'Save Date Detail', css_class='btn-primary mt-3')
        )
        self.helper.form_method = 'post'