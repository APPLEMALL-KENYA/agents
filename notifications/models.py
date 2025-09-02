from django.db import models
from django.conf import settings
from django.core.mail import send_mail


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    title = models.CharField(max_length=255, blank=True, null=True)  # optional
    link = models.URLField(blank=True, null=True)  # optional deep link
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - {self.message[:20]}"


# --- Helper Function ---
def create_notification(user, title, message, link=None, email=True, sms=False):
    notif = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )

    # send email
    if email and user.email:
        send_mail(
            subject=title or "New Notification",
            message=message,
            from_email="noreply@dropagent.com",
            recipient_list=[user.email],
            fail_silently=True,
        )

    # send SMS (stub - replace with Twilio/Africa’s Talking later)
    if sms:
        print(f"[SMS to {user.username}] {message}")

    return notif
