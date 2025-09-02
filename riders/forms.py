from django import forms

class ParcelScanForm(forms.Form):
    reference = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'readonly':'readonly'}))
