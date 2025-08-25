"""
URL configuration for dropagent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from agents import views
from django.utils import timezone
timezone.now
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from agent_portal import views as agent_views



from django.contrib import admin
from django.urls import path, include
from agents import views  # your main views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Root → Sign up page
    path('', views.register_agent, name='register'),  

    # Login page (if separate)
    path('login/', views.agent_login, name='login'),

    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Password Reset
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name="password_reset"),
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), 
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), 
         name="password_reset_confirm"),
    path("reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
         name="password_reset_complete"),

    # Agents app URLs
    path('agents/', include('agents.urls')),  

    # Agent portal URLs
    path('agent/', include('agent_portal.urls')),

    # Shops and parcels
    path('shops/', views.shops, name='shops'),
    path('parcel/search/', views.parcel_search, name='parcel_search'),
    path('add-parcel/', views.add_parcel, name='add_parcel'),
    path('parcel/<str:tracking_code>/', views.parcel_detail, name='parcel_detail'),
    path('parcel/receive/', views.parcel_receive, name='parcel_receive'),

]
