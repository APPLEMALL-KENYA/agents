from django.db import models

# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Roles(models.TextChoices):
 SUPERADMIN = "SUPERADMIN", _("Superadmin")
 AGENT = "AGENT", _("Agent")
 SUBAGENT = "SUBAGENT", _("Subagent")
 CUSTOMER = "CUSTOMER", _("Customer")
 RIDERS = "RIDERS", _("riders")


class User(AbstractUser):
 role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)


from django.db import models
from django.conf import settings

class AgentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_agents"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

from django.conf import settings
from django.db import models

from django.db import models


