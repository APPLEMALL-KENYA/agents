from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, AgentProfile, Roles


class AgentUserCreateForm(UserCreationForm):
  role = forms.ChoiceField(choices=[(Roles.AGENT, "Agent"), (Roles.SUBAGENT, "Subagent")])


class Meta:
 model = User
 fields = ("username", "email", "role")


class AgentProfileForm(forms.ModelForm):
 class Meta:
  model = AgentProfile
fields = ("phone", "location", "parent", "is_active")