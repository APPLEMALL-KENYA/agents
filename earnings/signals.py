# earnings/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AgentDeliveryRecord, DeliveryEarning
from notifications.models import Notification

@receiver(post_save, sender=AgentDeliveryRecord)
def notify_on_successful_delivery(sender, instance, created, **kwargs):
    if instance.successful:
        # Get delivery earning (assume created elsewhere)
        try:
            earning = DeliveryEarning.objects.get(delivery=instance)
        except DeliveryEarning.DoesNotExist:
            return
        
        # Notify agent
        Notification.objects.create(
            user=instance.agent.user,
            message=f"Delivery recorded. You earned Ksh {earning.amount}."
        )

        # Notify parent agent if exists
        if instance.agent.parent_agent:
            Notification.objects.create(
                user=instance.agent.parent_agent.user,
                message=f"You earned referral commission from {instance.agent.user.username}'s delivery."
            )
