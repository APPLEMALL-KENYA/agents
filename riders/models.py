from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import models
from parcels.models import Parcel  # Ensure Parcel model exists

# -------------------------
# Rider profile
# -------------------------# riders/models.py
from decimal import Decimal
from django.conf import settings
from django.db import models
from parcels.models import Parcel

# -------------------------
# Rider profile
# -------------------------
class RiderProfile(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('PROBATION', 'Probation'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    rating = models.FloatField(default=0.0)
    total_jobs = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


# -------------------------
# Available jobs to bid
# -------------------------
class AvailableJob(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    min_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('60.00'))  # Optional

    def __str__(self):
        return f"Parcel {self.parcel.reference} available"


# -------------------------
# Job accepted by rider (ongoing)
# -------------------------
class Job(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('ARRIVED', 'Arrived at Pickup Agent'),
        ('DELIVERED', 'Delivered'),
    ]

    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE)
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('60.00'))
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.parcel.reference} → {self.rider.user.username}"


# -------------------------
# Ratings given to riders
# -------------------------
class RiderRating(models.Model):
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE, related_name='ratings')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update rider's average rating
        all_ratings = self.rider.ratings.all()
        if all_ratings.exists():
            avg_rating = sum(r.rating for r in all_ratings) / all_ratings.count()
            self.rider.rating = avg_rating
            self.rider.save()


# -------------------------
# Rider wallet for earnings
# -------------------------
class RiderWallet(models.Model):
    rider = models.OneToOneField(RiderProfile, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def add_earning(self, km_travelled):
        if not isinstance(km_travelled, Decimal):
            km_travelled = Decimal(km_travelled)
        self.balance += Decimal('60.00') * km_travelled  # 60 KSH per km
        self.save()

    def withdraw(self, amount):
        """
        Withdraw money from the rider's wallet and create a notification.

        Args:
            amount (Decimal, float, or str): The amount to withdraw.

        Raises:
            ValueError: If the amount is greater than the current balance or non-positive.
        """
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(amount)
            except (InvalidOperation, TypeError):
                raise ValueError("Invalid amount")

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero")

        if amount > self.balance:
            raise ValueError("Insufficient balance")

        self.balance -= amount
        self.save()

        # Create notification
        RiderNotification.objects.create(
            rider=self.rider,
            message=f"Wallet withdrawal of Ksh {amount:.2f} successful."
        )


# -------------------------
# Rider notifications
# -------------------------
class RiderNotification(models.Model):
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.rider.user.username}: {self.message[:50]}"
