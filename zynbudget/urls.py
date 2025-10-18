from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('setup/', include('setup.urls', namespace='setup')), # FIX: Added namespace='setup'
    path('data/', include('data_management.urls', namespace='data_management')), # ADDED new data module
    path('aum/', include('aum_management.urls', namespace='aum_management')), # ADDED new AUM module
    path('budget/', include('budget_input.urls', namespace='budget_input')), # ADDED new Budget Input module
    path('analysis/', include('analysis.urls', namespace='analysis')), # ADDED new Analysis module
    path('predictive/', include('predictive_analytics.urls', namespace='predictive_analytics')), # ADDED new Predictive Analytics module
]

# Add this for serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)