from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import AgentRegistrationForm, AgentLoginForm
from django.contrib import messages

def register(request):
    if request.method == "POST":
        form = AgentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("agent_auth:dashboard")
    else:
        form = AgentRegistrationForm()
    return render(request, "agent_auth/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AgentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("agent_auth:dashboard")
    else:
        form = AgentLoginForm()
    return render(request, "agent_auth/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("agent_auth:login")

def dashboard(request):
    return render(request, "agent_auth/dashboard.html")
