from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.superadmin_login, name="superadmin_login"),
    path("dashboard/", views.superadmin_dashboard, name="superadmin_dashboard"),
    path("logout/", views.superadmin_logout, name="superadmin_logout"),
]
