# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from parcels.models import Parcel
from earnings.models import WithdrawalRequest
from .models import create_notification

@receiver(post_save, sender=Parcel)
def parcel_created_notification(sender, instance, created, **kwargs):
    if created:
        # Notify agent
        create_notification(
            recipient=instance.agent.user,
            title="New Parcel Assigned",
            message=f"A new parcel #{instance.id} has been created for delivery."
        )
        # Notify customer
        create_notification(
            recipient=instance.customer.user,
            title="Your Parcel is Registered",
            message=f"Tracking number: {instance.tracking_number}. Destination: {instance.destination}."
        )

@receiver(post_save, sender=WithdrawalRequest)
def withdrawal_status_notification(sender, instance, **kwargs):
    status = "approved" if instance.is_approved else "rejected"
    create_notification(
        recipient=instance.agent.user,
        title="Withdrawal Update",
        message=f"Your withdrawal request of KES {instance.amount} has been {status}."
    )

# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from parcels.models import Parcel
from earnings.models import AgentDeliveryRecord
from .models import Notification

User = get_user_model()

def create_notification(user, message):
    """Helper to safely create notification if user exists."""
    if user:
        Notification.objects.create(user=user, message=message)

# --- PARCEL CREATED ---
@receiver(post_save, sender=Parcel)
def parcel_created_notification(sender, instance, created, **kwargs):
    if created:
        # Notify agent
        if instance.assigned_agent and instance.assigned_agent.user:
            create_notification(
                instance.assigned_agent.user,
                f"📦 New parcel assigned: {instance.tracking_number} → {instance.destination}"
            )
        # Notify customer
        if instance.customer:
            create_notification(
                instance.customer,
                f"📦 Your parcel {instance.tracking_number} has been created. Destination: {instance.destination}"
            )

# --- DELIVERY SUCCESS ---
@receiver(post_save, sender=AgentDeliveryRecord)
def delivery_success_notification(sender, instance, created, **kwargs):
    if created and instance.successful:
        # Notify agent
        if instance.agent.user:
            create_notification(
                instance.agent.user,
                f"✅ Delivery recorded! You earned commission for {instance.parcel.tracking_number}"
            )
        # Notify parent agent
        if instance.agent.parent_agent and instance.agent.parent_agent.user:
            create_notification(
                instance.agent.parent_agent.user,
                f"💰 You earned 5% commission from your sub-agent {instance.agent.name}'s delivery."
            )

# notifications/signals.py
import logging
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse

logger = logging.getLogger(__name__)

def get_parcel_model():
    return apps.get_model("parcels", "Parcel")

@receiver(post_save, dispatch_uid="parcel_created_notification")
def parcel_created_notification(sender, instance, created, **kwargs):
    Parcel = get_parcel_model()
    # only handle Parcel saves
    if sender != Parcel:
        return
    if not created:
        return

    parcel = instance
    # try to pick a human-friendly identifier
    identifier = getattr(parcel, "tracking_number", None) or getattr(parcel, "id", None)

    # potential FK names to check on Parcel
    fk_names = [
        "agent", "assigned_to", "delivery_agent", "pickup_agent",
        "agent_profile", "owner", "user", "created_by"
    ]

    recipient_obj = None

    # try attribute names first (object or None)
    for name in fk_names:
        if hasattr(parcel, name):
            recipient_obj = getattr(parcel, name)
            if recipient_obj:
                break

    # if still nothing, check for *_id style fields and try to resolve to a User
    if not recipient_obj:
        for name in fk_names:
            id_attr = f"{name}_id"
            val = getattr(parcel, id_attr, None)
            if val:
                # we'll try to resolve below
                recipient_obj = val
                break

    User = get_user_model()
    target_user = None

    # If recipient_obj is an integer id, try fetching user by PK
    if isinstance(recipient_obj, int):
        try:
            target_user = User.objects.get(pk=recipient_obj)
        except User.DoesNotExist:
            target_user = None

    else:
        # if it's an AgentProfile instance (in users app)
        try:
            AgentProfile = apps.get_model("users", "AgentProfile")
            if AgentProfile and isinstance(recipient_obj, AgentProfile):
                target_user = getattr(recipient_obj, "user", None)
        except Exception:
            # model might not exist or import issues — ignore
            pass

        # if it's already a User instance
        if target_user is None and isinstance(recipient_obj, User):
            target_user = recipient_obj

        # if it's some object with .user attribute (e.g., profile)
        if target_user is None and hasattr(recipient_obj, "user"):
            possible_user = getattr(recipient_obj, "user")
            if isinstance(possible_user, User):
                target_user = possible_user
            elif isinstance(possible_user, int):
                try:
                    target_user = User.objects.get(pk=possible_user)
                except User.DoesNotExist:
                    target_user = None

    if not target_user:
        logger.info("parcel_created_notification: no user found for parcel %s; skipping notification", identifier)
        return

    # Build notification content
    title = f"Parcel #{identifier} created" if identifier else "New parcel created"
    message = f"You have been assigned a new parcel ({identifier})." if identifier else "You have been assigned a new parcel."

    # try using your helper create_notification(user, title, message, link=...)
    try:
        # helper should be in notifications.models (or move it to notifications.utils)
        from notifications.models import create_notification
        link = None
        try:
            # admin edit link for convenience (works in dev)
            link = reverse("admin:parcels_parcel_change", args=[parcel.pk])
        except Exception:
            link = None

        create_notification(target_user, title, message, link=link, email=True, sms=False)
        return
    except Exception as e:
        logger.debug("create_notification helper not available or failed: %s", e)

    # fallback: create Notification record directly
    try:
        Notification = apps.get_model("notifications", "Notification")
        if Notification:
            Notification.objects.create(user=target_user, message=message)
            return
    except Exception as ex:
        logger.exception("Failed to create fallback notification for parcel %s: %s", identifier, ex)
