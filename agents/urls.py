from django.urls import path
from . import views

app_name = "agents"  # <-- this sets the namespace

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('shops/', views.shops, name='shops'),
    path('add-parcel/', views.add_parcel, name='add_parcel'),  # ← must exist
    path('parcel/search/', views.parcel_search, name='parcel_search'),
    path('parcels/', views.parcel_list, name='parcel_list'),  # ← add this
    path('parcel/<str:tracking_code>/', views.parcel_detail, name='parcel_detail'),
    path('parcel/receive/', views.parcel_receive, name='parcel_receive'),
]
