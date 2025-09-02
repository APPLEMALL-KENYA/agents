"""
URL configuration for dropagent project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from dashboard import views 

# App-specific imports
from parcels.views import track_parcel_view
from users.views import (
    RoleLoginView,
    SuperadminDashboardView,
    ClientDashboardView,
    AgentDashboardView,
    RiderDashboardView,
)

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # Dashboards
    path("superadmin/", include("dashboard.urls")),
    path("dashboard/client/", ClientDashboardView.as_view(), name="client_dashboard"),
    path("dashboard/agent/", AgentDashboardView.as_view(), name="agent_dashboard"),
    path("dashboard/rider/", RiderDashboardView.as_view(), name="rider_dashboard"),
    path("dashboard/", include("dashboard.urls")),  # extra dashboard URLs

    # Authentication
    path("accounts/", include("django.contrib.auth.urls")),  # default auth views
    path("login/", RoleLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Parcel tracking (public)
    path("track-parcel/", track_parcel_view, name="track_parcel"),

    # Riders
    path("riders/", include("riders.urls")),
]
