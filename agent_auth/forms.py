from django import forms
from .models import AgentUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class AgentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    shop_name = forms.CharField(required=True)
    shop_location = forms.CharField(required=True)

    class Meta:
        model = AgentUser
        fields = ["username", "email", "phone", "shop_name", "shop_location", "password1", "password2"]

class AgentLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput)
