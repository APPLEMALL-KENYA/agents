from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AgentUser

class AgentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)

    class Meta:
        model = AgentUser
        fields = ['username', 'email', 'phone', 'shop', 'password1', 'password2']
