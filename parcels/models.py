# parcels/models.py
from django.dispatch import receiver
from django.utils import timezone
import uuid
from django.db import models
from django.conf import settings
from parcels.utils import generate_qr_code, send_custom_email
from shops.models import Shop
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    PARTIAL = "partial", "Partial"


DISPATCH_METHOD_CHOICES = [
        ("hq_to_shop", "HQ to Shop"),
        ("matatu_direct", "Matatu Direct"),
    ]

CREATED = "CREATED", "Created"
IN_TRANSIT = "IN_TRANSIT", "In Transit"
DELIVERED = "DELIVERED", "Delivered"
CANCELLED = "CANCELLED", "Cancelled"



class PaymentMethod(models.TextChoices):
    BEFORE_DISPATCH = "BEFORE_DISPATCH", "Before Dispatch"
    ON_COLLECTION = "ON_COLLECTION", "On Collection"
    CASH = "CASH", "Cash"
    MPESA = "MPESA", "M-Pesa"
    BANK = "BANK", "Bank Transfer"
    CARD = "CARD", "Credit/Debit Card"
    NONE = "NONE", "Not Applicable"


class PaymentType(models.TextChoices):
    FULL_AMOUNT = "FULL_AMOUNT", "Full Amount"
    DELIVERY_COST = "DELIVERY_COST", "Delivery Cost Only"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name



class ParcelStatus(models.TextChoices):
    CREATED = "created", "Created"
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"
    RETURNED = "returned", "Returned"
    CANCELLED = "cancelled", "Cancelled"

class Parcel(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Pickup'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED_PICKUP', 'Arrived at Pickup Agent'),
        ('DELIVERED', 'Delivered to Client'),
    ]

class Parcel(models.Model):
    # Identifiers
    tracking_number = models.CharField(max_length=100, unique=True, blank=True)
    reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    matatu_direct = models.BooleanField(default=False, help_text="Was parcel dispatched directly via matatu?")

    # Customer details
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    destination = models.CharField(max_length=255)

    # Costs & Payments
    value_kes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    full_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # set by superuser
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING

    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.ON_COLLECTION
    )
    payment_type = models.CharField(
        max_length=20, choices=PaymentType.choices, default=PaymentType.DELIVERY_COST
    )

    # Dispatch details
    dispatch_from = models.CharField(max_length=255, blank=True, null=True)  # e.g., HQ
    dispatch_to = models.CharField(max_length=255, blank=True, null=True)    # e.g., Pickup Shop
    via_matatu = models.BooleanField(default=False, help_text="Send directly to client (no shop).")

    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    origin_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="parcels_created"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parcels_assigned"
    )

    # Status
    status = models.CharField(
        max_length=20, choices=ParcelStatus.choices, default=ParcelStatus.CREATED
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
    max_length=20,
    choices=ParcelStatus.choices,
    default=ParcelStatus.CREATED,
)


    def save(self, *args, **kwargs):
        if not self.tracking_number:
            # Generate a unique tracking number
            self.tracking_number = str(uuid.uuid4()).replace('-', '')[:12].upper()
        super().save(*args, **kwargs)
    
class Receipt(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="receipts")
    issued_at = models.DateTimeField(default=timezone.now)
    receipt_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    updated_at = models.DateTimeField(auto_now=True)  # <-- add this


    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)




class DeliveryNote(models.Model):
    parcel = models.OneToOneField("Parcel", on_delete=models.CASCADE, related_name="delivery_note")
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate QR content (could be tracking URL or parcel ID)
        qr_data = f"Parcel ID: {self.parcel.id}, Status: {self.parcel.status}"
        
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        file_name = f"parcel-{self.parcel.id}-qr.png"
        
        self.qr_code.save(file_name, File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery Note for Parcel {self.parcel.id}" 

class Invoice(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    issued_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

@receiver(post_save, sender=Parcel)
def handle_parcel_creation(sender, instance, created, **kwargs):
    if created:
        # Determine recipient email safely
        recipient_email = None
        if hasattr(instance, 'user') and instance.user:
            recipient_email = getattr(instance.user, 'email', None)
        # Optional: if you ever add a 'customer' field
        elif hasattr(instance, 'customer') and instance.customer:
            recipient_email = getattr(instance.customer, 'email', None)

        # Generate invoice if unpaid
        if instance.payment_status == "UNPAID":
            Invoice.objects.get_or_create(parcel=instance)
            if recipient_email:
                send_custom_email(
                    recipient_email,
                    "Invoice Created",
                    f"Invoice for parcel {instance.reference}"
                )
        else:
            # Generate receipt if paid
            Receipt.objects.get_or_create(parcel=instance, defaults={"amount": getattr(instance, 'amount', 0)})
            if recipient_email:
                send_custom_email(
                    recipient_email,
                    "Payment Receipt",
                    f"Receipt for parcel {instance.reference}"
                )

        # Always create delivery note with QR
        note, _ = DeliveryNote.objects.get_or_create(parcel=instance)
        generate_qr_code(note)
