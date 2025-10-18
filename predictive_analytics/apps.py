# predictive_analytics/apps.py
from django.apps import AppConfig

class PredictiveAnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictive_analytics'
    verbose_name = 'Predictive Analytics'