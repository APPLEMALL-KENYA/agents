from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Roles, AgentProfile


@receiver(post_save, sender=User)
def create_agent_profile(sender, instance, created, **kwargs):
  if created and instance.role in (Roles.AGENT, Roles.SUBAGENT):
   AgentProfile.objects.create(user=instance)