# parcels/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Parcel, Invoice, Receipt, DeliveryNote
from .utils import generate_qr_code, send_custom_email
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Parcel)
def handle_parcel_creation(sender, instance, created, **kwargs):
    if created:
        if instance.payment_status == "UNPAID":
            Invoice.objects.get_or_create(parcel=instance)
            if instance.customer and instance.customer.email:
                send_custom_email(
                    instance.customer.email,
                    "Invoice Created",
                    f"Invoice for parcel {instance.reference}"
                )
        else:
            # Generate receipt if paid
            Receipt.objects.get_or_create(parcel=instance, defaults={"amount": getattr(instance, 'amount', 0)})
            if instance.customer and instance.customer.email:
                send_custom_email(
                    instance.customer.email,
                    "Payment Receipt",
                    f"Receipt for parcel {instance.reference}"
                )

        # Always create delivery note with QR
        note, _ = DeliveryNote.objects.get_or_create(parcel=instance)
        generate_qr_code(note)
