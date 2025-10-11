from django.urls import path
from . import views

# FIX: Add app_name to resolve ImproperlyConfigured error with namespace
app_name = 'setup'

urlpatterns = [
    # Index
    path('', views.setup_index, name='setup_index'),
    
    # RSA Fund URLs
    path('rsafund/', views.RSAFundListView.as_view(), name='rsafund_list'),
    path('rsafund/new/', views.RSAFundCreateView.as_view(), name='rsafund_create'),
    path('rsafund/<int:pk>/edit/', views.RSAFundUpdateView.as_view(), name='rsafund_update'),
    path('rsafund/<int:pk>/delete/', views.RSAFundDeleteView.as_view(), name='rsafund_delete'),
    
    # State URLs
    path('state/', views.StateListView.as_view(), name='state_list'),
    path('state/new/', views.StateCreateView.as_view(), name='state_create'),
    path('state/<int:pk>/edit/', views.StateUpdateView.as_view(), name='state_update'),
    path('state/<int:pk>/delete/', views.StateDeleteView.as_view(), name='state_delete'),
    
    # Location URLs
    path('location/', views.LocationListView.as_view(), name='location_list'),
    path('location/new/', views.LocationCreateView.as_view(), name='location_create'),
    path('location/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_update'),
    path('location/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
    
    # Region URLs
    path('region/', views.RegionListView.as_view(), name='region_list'),
    path('region/new/', views.RegionCreateView.as_view(), name='region_create'),
    path('region/<int:pk>/edit/', views.RegionUpdateView.as_view(), name='region_update'),
    path('region/<int:pk>/delete/', views.RegionDeleteView.as_view(), name='region_delete'),
    
    # Managed Fund URLs
    path('managedfund/', views.ManagedFundListView.as_view(), name='managedfund_list'),
    path('managedfund/new/', views.ManagedFundCreateView.as_view(), name='managedfund_create'),
    path('managedfund/<int:pk>/edit/', views.ManagedFundUpdateView.as_view(), name='managedfund_update'),
    path('managedfund/<int:pk>/delete/', views.ManagedFundDeleteView.as_view(), name='managedfund_delete'),
    
    # Date Detail URLs
    path('datedetail/', views.DateDetailListView.as_view(), name='date_detail_list'),
    path('datedetail/new/', views.DateDetailCreateView.as_view(), name='date_detail_create'),
    path('datedetail/<int:pk>/edit/', views.DateDetailUpdateView.as_view(), name='date_detail_update'),
    path('datedetail/<int:pk>/delete/', views.DateDetailDeleteView.as_view(), name='date_detail_delete'),
]