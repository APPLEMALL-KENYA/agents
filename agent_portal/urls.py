from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_agent, name="agent_register"),
    path("login/", views.login_agent, name="agent_login"),
    path("dashboard/", views.dashboard, name="agent_dashboard"),
]
