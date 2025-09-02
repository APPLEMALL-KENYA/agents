# earnings/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class AgentCommissionRule(models.Model):
    """Superadmin-defined commission % per category"""
    category = models.CharField(max_length=100, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission % for deliveries in this category")

    def __str__(self):
        return f"{self.category} - {self.percentage}%"


class DeliveryEarning(models.Model):
    """Tracks per-delivery earnings for agents"""
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="delivery_earnings")
    parcel = models.ForeignKey("parcels.Parcel", on_delete=models.CASCADE, related_name="earnings")
    category = models.CharField(max_length=100)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)  # flat KES 50
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def calculate_total(self):
        """Compute commission + base"""
        try:
            rule = AgentCommissionRule.objects.get(category=self.category)
            self.commission_amount = (rule.percentage / 100) * self.base_amount
        except AgentCommissionRule.DoesNotExist:
            self.commission_amount = 0
        self.total_amount = self.base_amount + self.commission_amount
        return self.total_amount

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Earning {self.total_amount} for {self.agent}"


class SubAgentCommission(models.Model):
    """5% commission override to parent when subagent earns"""
    parent_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subagent_commissions")
    subagent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="earned_commissions")
    delivery_earning = models.ForeignKey(DeliveryEarning, on_delete=models.CASCADE, related_name="subagent_bonus")
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def calculate_bonus(self):
        self.bonus_amount = (5 / 100) * self.delivery_earning.total_amount
        return self.bonus_amount

    def save(self, *args, **kwargs):
        self.calculate_bonus()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent_agent} bonus {self.bonus_amount} from {self.subagent}"


class WithdrawalRequest(models.Model):
    """Redeem earnings: cash (>=500) or Applemall credit (<500)"""
    REDEEM_CHOICES = [
        ("cash", "Cash"),
        ("applemall_credit", "Applemall Credit"),
    ]

    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    redeem_type = models.CharField(max_length=20, choices=REDEEM_CHOICES)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount < 500 and self.redeem_type != "applemall_credit":
            raise ValidationError("Earnings below 500 can only be redeemed as Applemall credit.")
        if self.amount >= 500 and self.redeem_type != "cash":
            raise ValidationError("Earnings above or equal to 500 must be redeemed as cash.")

    def __str__(self):
        return f"{self.agent} requested {self.amount} via {self.redeem_type}"

class AgentDeliveryRecord(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deliveries")
    parcel = models.ForeignKey("parcels.Parcel", on_delete=models.CASCADE, related_name="delivery_records")
    delivered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.agent} delivered {self.parcel} on {self.delivered_at}"

from users.models import AgentProfile
from django.db import models

class Earning(models.Model):
    agent = models.ForeignKey(
        "users.AgentProfile",   # using string reference is safest
        on_delete=models.CASCADE,
        related_name="earnings"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent.user.username} - {self.amount}"

