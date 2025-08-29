# agents/utils/email_service.py
from django.core.mail import send_mail

def send_account_summary_email(to_email, name, phone, email, shop_name=None, shop_location=None):
    """
    Sends a summary email to the newly registered agent.
    """
    subject = "Applemall Agent Account Created"
    message = f"""
    Hello {name},

    Your agent account has been created successfully.

    Details:
    Phone: {phone}
    Email: {email}
    """
    if shop_name and shop_location:
        message += f"\nShop Name: {shop_name}\nShop Location: {shop_location}"

    message += "\n\nThank you for joining Applemall!"

    send_mail(
        subject=subject,
        message=message,
        from_email="appleonlinemall33@gmail.com",
        recipient_list=[to_email],
        fail_silently=False,
    )


def send_custom_email(subject, message, to_email, template_name=None, context=None):
    """
    Generic email sender (fallback for templates).
    """
    send_mail(
        subject,
        message or "",
        "appleonlinemall33@gmail.com",
        [to_email],
        fail_silently=False,
    )

