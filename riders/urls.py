from django.urls import path
from . import views
from riders import views as rider_views  # <- THIS is the alias


urlpatterns = [
    # Rider dashboard
    path('dashboard/', views.rider_dashboard, name='rider_dashboard'),

    # Scan pickup/delivery
    path('scan/pickup/', views.scan_pickup, name='scan_pickup'),
    path('scan/delivery/', views.scan_delivery, name='scan_delivery'),
    path('scan/parcel/<int:parcel_id>/', views.scan_parcel, name='scan_parcel'),

    # Superadmin routes
    path('admin/dashboard/', views.rider_dashboard_admin, name='rider_dashboard_admin'),
    path('admin/rider/<int:rider_id>/suspend/', views.suspend_rider, name='suspend_rider'),
    path('admin/rider/<int:rider_id>/edit/', views.edit_rider, name='edit_rider'),
    path('register/', rider_views.register_rider, name='register_rider'),
    path('withdraw/', views.withdraw_request, name='withdraw_request'),

]
