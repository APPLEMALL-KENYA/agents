# earnings/apps.py
from django.apps import AppConfig

class EarningsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'earnings'
    label = "earnings"

    def ready(self):
        import earnings.signals
