from django.shortcuts import render, redirect, get_object_or_404
from .models import Agent, Parcel, Shop
from .forms import AgentForm, ParcelForm
from agent_portal.forms import AgentRegisterForm
from django.contrib.auth import login

# --- Agents ---
def add_agent(request):
    if request.method == "POST":
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agents:agent_list')
    else:
        form = AgentForm()
    return render(request, "agents/add_agent.html", {"form": form})

def agent_list(request):
    agents = Agent.objects.all()
    return render(request, "agents/agent_list.html", {"agents": agents})

# --- Parcels ---
def add_parcel(request):
    if request.method == "POST":
        form = ParcelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agents:parcel_list')
    else:
        form = ParcelForm()
    return render(request, "agents/add_parcel.html", {"form": form})

def parcel_list(request):
    parcels = Parcel.objects.all()
    return render(request, "agents/parcel_list.html", {"parcels": parcels})

def parcel_search(request):
    query = request.GET.get('q', '')
    parcels = Parcel.objects.filter(tracking_code__icontains=query) if query else []
    return render(request, 'parcel_search.html', {'parcels': parcels, 'query': query})

def parcel_detail(request, tracking_code):
    parcel = get_object_or_404(Parcel, tracking_code=tracking_code)
    return render(request, 'parcel_detail.html', {'parcel': parcel})

def parcel_receive(request):
    if request.method == 'POST':
        # Implement parcel receiving logic here
        pass
    return render(request, 'parcel_receive.html')

# --- Shops ---
def shops(request):
    all_shops = Shop.objects.all()
    return render(request, 'agents/shops.html', {'shops': all_shops})

# --- Dashboard ---
def dashboard(request):
    return render(request, 'dashboard.html')

# --- Agent registration ---
def register_agent(request):
    if request.method == "POST":
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AgentRegisterForm()
    return render(request, 'agents/register.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.contrib import messages

def agent_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # after login
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'agents/login.html')
