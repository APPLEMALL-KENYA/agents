from django import forms
from .models import Agent, Parcel, Shop

from django import forms
from .models import Agent, Shop

from django import forms
from .models import Agent, Shop

from django import forms
from django.contrib.auth.models import User
from .models import Agent, Shop

class AgentForm(forms.ModelForm):
    parent_reference = forms.CharField(required=False, label="Parent Agent Reference Code")
    shop_name = forms.CharField(required=False, label="Shop Name")
    shop_location = forms.CharField(required=False, label="Shop Location")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Agent
        fields = ['name', 'phone', 'email', 'is_shop']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        is_shop = cleaned_data.get("is_shop")
        shop_name = cleaned_data.get("shop_name")
        shop_location = cleaned_data.get("shop_location")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if is_shop and (not shop_name or not shop_location):
            raise forms.ValidationError("Shop name and location required for shop agents")

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")

        # Create a user account
        user = User.objects.create_user(
            username=cleaned_data['email'],
            email=cleaned_data['email'],
            password=password,
            first_name=cleaned_data['name']
        )

        agent = super().save(commit=False)
        agent.user = user

        # Handle parent reference
        code = cleaned_data.get('parent_reference')
        if code:
            try:
                parent = Agent.objects.get(reference_code=code)
                agent.parent_agent = parent
            except Agent.DoesNotExist:
                pass  

        if commit:
            agent.save()
            if agent.is_shop:
                Shop.objects.create(
                    name=cleaned_data.get('shop_name'),
                    location=cleaned_data.get('shop_location')
                )

        return agent



class ParcelForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ['shop', 'agent', 'tracking_code', 'sender_name', 'receiver_name', 'receiver_phone', 'status']
