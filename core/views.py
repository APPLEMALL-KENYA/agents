from django.shortcuts import render

# Create your views here.
# core/views.py
from django.shortcuts import render
from parcels.models import Parcel

def home(request):
    query = request.GET.get("q")
    parcels = None
    if query:
        parcels = Parcel.objects.filter(reference__icontains=query)
    return render(request, "core/home.html", {"parcels": parcels})
