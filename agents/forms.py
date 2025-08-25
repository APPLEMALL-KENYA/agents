from django import forms
from .models import Agent, Parcel, Shop

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['shop', 'name', 'phone', 'email', 'active']

class ParcelForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ['shop', 'agent', 'tracking_code', 'sender_name', 'receiver_name', 'receiver_phone', 'status']
