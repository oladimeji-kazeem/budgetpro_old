from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, 
    PasswordResetView, PasswordResetConfirmView
)
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('dashboard') # Changed from 'home' to 'dashboard'

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Changed redirect from 'home' to 'dashboard'
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard') # Changed redirect from 'home' to 'dashboard'
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

# New public view for the root URL
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    # This renders the public landing page (home.html)
    return render(request, 'accounts/home.html') 

# New protected view for the dashboard
@login_required
def dashboard_view(request):
    # This renders the authenticated dashboard page (dashboard.html)
    return render(request, 'accounts/dashboard.html')