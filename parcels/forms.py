# parcels/forms.py
from django import forms
from .models import Parcel


class ParcelForm(forms.ModelForm):
  class Meta:
   model = Parcel
   fields = ( "tracking_number", "banner_image_url", "customer_name", "customer_email",
            "destination", "value_kes", "category", "origin_shop", "assigned_to", "status" )