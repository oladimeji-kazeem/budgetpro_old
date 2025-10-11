from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'full_name', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'email')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)