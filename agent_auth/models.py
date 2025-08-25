from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class AgentUser(AbstractUser):
    # Add any custom fields you want for agents
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
