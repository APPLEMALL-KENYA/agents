from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "agents"

urlpatterns = [
    # Dashboard
    path("", views.dashboard_view, name="dashboard"),   # ✅ unified

    # Shops
    path("shops/", views.shops, name="shops"),
    path("agents/", views.agent_list, name="agent_list"),

    # Parcels
    path("add-parcel/", views.add_parcel, name="add_parcel"),
    path("parcel/search/", views.parcel_search, name="parcel_search"),
    path("parcels/", views.parcel_list, name="parcel_list"),
    path("parcel/<str:tracking_code>/", views.parcel_detail, name="parcel_detail"),
    path("parcel/receive/", views.parcel_receive, name="parcel_receive"),

    # Agent Registration & Login
    path("add/", views.add_agent, name="add_agent"),
    path("register/", views.add_agent, name="register"),
    path("login/", views.agent_login, name="login"),

    # Logout
    path("logout/", LogoutView.as_view(next_page="agents:login"), name="logout"),
]
