# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from decimal import Decimal

# ------------------------------
# Shops
# ------------------------------
class Shop(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200, default="Nairobi")
    phone = models.CharField(max_length=20, blank=True, null=True, default="0714680792")
    email = models.EmailField(blank=True, null=True, default="info@applemall.co.ke")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ------------------------------
# Agents
# ------------------------------
import uuid
from django.db import models
from django.contrib.auth.models import User

def generate_unique_reference():
    """Generate a unique 6-character reference code for an agent."""
    while True:
        code = uuid.uuid4().hex[:6].upper()
        if not Agent.objects.filter(reference_code=code).exists():
            return code
from django.db import models
from django.contrib.auth.models import User
from .utils import generate_unique_reference  # make sure you still have this

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent")
    name = models.CharField(max_length=255, default="New Agent")
    phone = models.CharField(max_length=20, blank=True, null=True, default="0714680792")
    email = models.EmailField(blank=True, null=True, default="agent@example.com")
    reference_code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_unique_reference
    )
    parent_agent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referred_agents"
    )
    is_shop = models.BooleanField(default=False)
    commission_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def username(self):
        """Shortcut to get linked user’s username (usually email)."""
        return self.user.username

    @property
    def has_parent(self):
        """Check if this agent was referred by another."""
        return self.parent_agent is not None



# ------------------------------
# Parcels
# ------------------------------
class Parcel(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="parcels", null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="parcels")
    tracking_code = models.CharField(max_length=50, unique=True)
    sender_name = models.CharField(max_length=150)
    receiver_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=20, default="0714680792")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tracking_code} - {self.status}"


# ------------------------------
# forms.py
# ------------------------------
from django import forms

class AgentForm(forms.ModelForm):
    reference_code_input = forms.CharField(
        required=False,
        help_text="Enter the reference code of the parent agent, if any"
    )

    class Meta:
        model = Agent
        fields = ['name', 'phone', 'email', 'is_shop']

    def save(self, commit=True):
        agent = super().save(commit=False)
        code = self.cleaned_data.get('reference_code_input')
        if code:
            try:
                parent = Agent.objects.get(reference_code=code)
                agent.parent_agent = parent
            except Agent.DoesNotExist:
                pass  # optionally raise ValidationError
        if commit:
            agent.save()
        return agent


# ------------------------------
# views.py
# ------------------------------
from django.shortcuts import render, redirect
from .models import Parcel
from .forms import ParcelForm

def add_parcel(request):
    """
    View to create a new parcel.
    Parent agent gets commission if applicable.
    """
    if request.method == "POST":
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            # Set the agent creating the parcel
            parcel.agent = request.user.agent
            parcel.save()

            # Add commission to parent agent
            parent = request.user.agent.parent_agent
            if parent:
                commission_amount = Decimal('50')  # fixed or calculated
                parent.commission_balance += commission_amount
                parent.save()

            return redirect("agents:parcel_list")
    else:
        form = ParcelForm()
    return render(request, "agents/add_parcel.html", {"form": form})
