from django.db import models

# Create your models here.
# dashboards/models.py
from django.db import models
from django.contrib.auth.models import User
from django import views


class Dashboard(models.Model):
    """
    Stores aggregated analytics for SuperAdmin dashboard.
    Can be updated via signals or cron jobs.
    """
    total_agents = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    total_parcels = models.PositiveIntegerField(default=0)
    delivered_parcels = models.PositiveIntegerField(default=0)
    pending_parcels = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboard"

    def __str__(self):
        return f"Dashboard Stats (Updated: {self.updated_at})"
