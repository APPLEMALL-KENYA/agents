from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from agents import views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Dashboard (Root URL)
    path("", views.dashboard, name="dashboard"),

    # Agents app
    path("agents/", include("agents.urls")),

    # Shops and Parcels
    path("shops/", views.shops, name="shops"),
    path("parcel/search/", views.parcel_search, name="parcel_search"),
    path("parcel/add/", views.add_parcel, name="add_parcel"),
    path("parcel/<str:tracking_code>/", views.parcel_detail, name="parcel_detail"),
    path("parcel/receive/", views.parcel_receive, name="parcel_receive"),

    # Password Reset Flow
    path("password_reset/", 
         auth_views.PasswordResetView.as_view(template_name="agents/password_reset_form.html"), 
         name="password_reset"),
    path("password_reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="agents/password_reset_done.html"), 
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="agents/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    path("reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="agents/password_reset_complete.html"), 
         name="password_reset_complete"),
]
