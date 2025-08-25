from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import AgentRegisterForm
from django.contrib import messages

def register_agent(request):
    if request.method == "POST":
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("agent_login")
    else:
        form = AgentRegisterForm()
    return render(request, "agent_portal/register.html", {"form": form})

def login_agent(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("agent_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "agent_portal/login.html")

@login_required
def dashboard(request):
    return render(request, "agent_portal/dashboard.html")
