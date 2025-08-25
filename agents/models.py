from django.db import models
from django.utils import timezone


class Shop(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200, default="Nairobi")
    phone = models.CharField(max_length=20, blank=True, null=True, default="0714680792")
    email = models.EmailField(blank=True, null=True, default="info@applemall.co.ke")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Agent(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="agents",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, default="0714680792")
    email = models.EmailField(blank=True, null=True, default="info@applemall.co.ke")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.shop.name if self.shop else 'No Shop'})"


class Parcel(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
    ]

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="parcels",
        null=True,
        blank=True
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parcels"
    )
    tracking_code = models.CharField(max_length=50, unique=True)
    sender_name = models.CharField(max_length=150)
    receiver_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=20, default="0714680792")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tracking_code} - {self.status}"
