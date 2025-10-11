from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'John Doe'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'you@leadwaypension.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('full_name', 'email')