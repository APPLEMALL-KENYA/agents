# parcels/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("scan/<int:parcel_id>/", views.scan_qr, name="scan_qr"),
]
