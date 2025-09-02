# parcels/utils.py
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.core.files import File

def generate_qr_code(delivery_note):
    data = f"https://applemall.co.ke/parcel/{delivery_note.parcel.reference}/scan"
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    file_name = f"qr_{delivery_note.parcel.reference}.png"
    delivery_note.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=True)

from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list, from_email=None):
    """
    Simple wrapper around Django's send_mail.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
