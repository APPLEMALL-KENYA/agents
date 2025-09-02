# users/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from parcels.models import Parcel

class RoleLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return "/dashboard/superadmin/"
        elif user.role == "AGENT":
            return "/dashboard/agent/"
        elif user.role == "SUBAGENT":
            return "/dashboard/subagent/"
        elif user.role == "RIDERS":
            return "/dashboard/rider/"
        else:  # CUSTOMER
            return "/dashboard/client/"

# users/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class SuperadminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/superadmin_dashboard.html"

class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/client_dashboard.html"

class AgentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/agent_dashboard.html"

class RiderDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/rider_dashboard.html"

def client_dashboard(request):
    parcels = Parcel.objects.filter(customer=request.user)
    notifications = request.user.client_notifications.all()  # example related_name
    context = {
        'parcels': parcels,
        'notifications': notifications,
        'active_orders_count': parcels.filter(status__in=['IN_TRANSIT', 'DISPATCHED']).count(),
        'delivered_parcels_count': parcels.filter(status='DELIVERED').count(),
        'cancelled_parcels_count': parcels.filter(status='CANCELLED').count(),
        'searched': False,
    }
    return render(request, 'dashboards/client_dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def role_login_view(request):
    tracked_parcel = None
    searched = False

    if request.method == "POST":
        role = request.POST.get("role")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect based on role
            if role == "client":
                return redirect("client_dashboard")
            elif role == "rider":
                return redirect("rider_dashboard")
            elif role == "agent":
                return redirect("agent_dashboard")
            elif role == "superadmin":
                return redirect("superadmin_dashboard")
            else:
                messages.error(request, "Invalid role selected.")
        else:
            messages.error(request, "Invalid username or password.")

    # Handle guest parcel search
    reference = request.GET.get("reference")
    if reference:
        searched = True
        from parcels.models import Parcel
        try:
            tracked_parcel = Parcel.objects.get(reference=reference)
        except Parcel.DoesNotExist:
            tracked_parcel = None

    return render(request, "login.html", {
        "tracked_parcel": tracked_parcel,
        "searched": searched,
        "role": request.POST.get("role", "client"),
    })


# --- Helper to check superadmin role ---


