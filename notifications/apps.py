from django.apps import AppConfig

class EarningsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"  # must match folder name

    def ready(self):
        import earnings.signals  # noqa
