from django.shortcuts import render

# Create your views here.
# parcels/views.py
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Parcel

def scan_qr(request, reference):
    parcel = get_object_or_404(Parcel, reference=reference)

    # Simple rule: update next status
    if parcel.status == "CREATED":
        parcel.status = "SHIPPING"
    elif parcel.status == "SHIPPING":
        parcel.status = "ARRIVED"
    elif parcel.status == "ARRIVED":
        parcel.status = "DELIVERED"

    parcel.save()
    return HttpResponse(f"Parcel {parcel.reference} status updated to {parcel.status}")

from django.shortcuts import render, get_object_or_404
from parcels.models import Parcel

def track_parcel_view(request):
    reference = request.GET.get('reference', '')
    tracked_parcel = None
    if reference:
        try:
            tracked_parcel = Parcel.objects.get(reference=reference)
        except Parcel.DoesNotExist:
            tracked_parcel = None

    return render(request, 'dashboards/client_dashboard.html', {
        'tracked_parcel': tracked_parcel,
    })
