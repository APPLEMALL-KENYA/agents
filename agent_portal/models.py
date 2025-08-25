# agent_portal/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class AgentUser(AbstractUser):
    # Any extra fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    shop = models.CharField(max_length=100, blank=True, null=True)  # If you want a shop field

    class Meta:
        verbose_name = "Agent User"
        verbose_name_plural = "Agent Users"

    # Optional: set related names to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='agentuser_set',  # unique name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='agentuser_set',  # unique name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
