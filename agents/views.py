# agents/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .utils import generate_unique_reference, send_account_summary_email, send_custom_email
from .models import Agent, Parcel, Shop
from .forms import AgentForm, ParcelForm

# ----------------------------
# Utilities with fallbacks
# ----------------------------
try:
    from .utils.generate import generate_unique_reference
except ImportError:
    # Fallback stub
    def generate_unique_reference():
        return "REF-UNKNOWN"

try:
    from .utils.email_service import send_account_summary_email
except ImportError:
    # Fallback minimal email sender
    def send_account_summary_email(to_email, name, phone, email, shop_name=None, shop_location=None):
        from django.core.mail import send_mail
        send_mail(
            "Applemall Account Created",
            f"Hello {name}, your account has been created successfully.",
            "appleonlinemall33@gmail.com",
            [to_email],
            fail_silently=False,
        )

# send_custom_email fallback
send_custom_email = None
try:
    from .utils.email_service import send_custom_email as _send_custom_email
    send_custom_email = _send_custom_email
except ImportError:
    try:
        from utils.email_service import send_custom_email as _send_custom_email
        send_custom_email = _send_custom_email
    except ImportError:
        # Local fallback
        from django.core.mail import send_mail as _send_mail
        def send_custom_email(subject, message, to_email, template_name=None, context=None):
            _send_mail(subject, message or "", "appleonlinemall33@gmail.com", [to_email], fail_silently=False)


# ================================================================
# AUTHENTICATION
# ================================================================
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Login successful")

            # Handle redirect after login
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("agents:dashboard")   # make sure you have this named URL
        else:
            messages.error(request, "Wrong credentials. Please try again.")
            return redirect("agents:login")       # keep consistent with your namespace
    else:
        form = AuthenticationForm()
    return render(request, "agents/login.html", {"form": form})


def agent_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("agents:dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "agents/login.html")


def agent_logout(request):
    auth_logout(request)
    return redirect("agents:login")


def custom_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered. Please sign up.")
            return redirect("register")
        user = authenticate(request, username=user.username, password=password)
        if user:
            auth_login(request, user)
            return redirect("agents:dashboard")
        else:
            messages.error(request, "Incorrect password. Forgot password?")
            return redirect("password_reset")
    return render(request, "agents/login.html")


# ================================================================
# DASHBOARD
# ================================================================
@login_required(login_url="login")
def dashboard(request):
    try:
        agent = Agent.objects.get(user=request.user)
    except Agent.DoesNotExist:
        agent = None
    return render(request, "agents/dashboard.html", {"agent": agent})


@login_required
def dashboard_view(request):
    return render(request, "agents/dashboard.html")


# ================================================================
# AGENTS
# ================================================================
def add_agent(request):
    if request.method == "POST":
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("agents:agent_list")
    else:
        form = AgentForm()
    return render(request, "agents/add_agent.html", {"form": form})


@login_required(login_url="login")
def agent_list(request):
    agents = Agent.objects.all()
    return render(request, "agents/agent_list.html", {"agents": agents})


def register_agent(request):
    if request.method == "POST":
        form = AgentForm(request.POST)
        if form.is_valid():
            agent = form.save()
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            is_shop = form.cleaned_data.get('is_shop')
            shop_name = form.cleaned_data.get('shop_name') if is_shop else None
            shop_location = form.cleaned_data.get('shop_location') if is_shop else None
            send_account_summary_email(
                to_email=email,
                name=name,
                phone=phone,
                email=email,
                shop_name=shop_name,
                shop_location=shop_location
            )
            return render(request, 'agents/register_success.html', {'agent': agent})
    else:
        form = AgentForm()
    return render(request, 'agents/register.html', {'form': form})


# ================================================================
# PARCELS
# ================================================================
@login_required(login_url="login")
def add_parcel(request):
    if request.method == "POST":
        form = ParcelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("agents:parcel_list")
    else:
        form = ParcelForm()
    return render(request, "agents/add_parcel.html", {"form": form})


@login_required(login_url="login")
def parcel_list(request):
    parcels = Parcel.objects.all()
    return render(request, "agents/parcel_list.html", {"parcels": parcels})


@login_required(login_url="login")
def parcel_search(request):
    query = request.GET.get("q", "")
    parcels = Parcel.objects.filter(tracking_code__icontains=query) if query else []
    return render(request, "agents/parcel_search.html", {"parcels": parcels, "query": query})


@login_required(login_url="login")
def parcel_detail(request, tracking_code):
    parcel = get_object_or_404(Parcel, tracking_code=tracking_code)
    return render(request, "agents/parcel_detail.html", {"parcel": parcel})


@login_required(login_url="login")
def parcel_receive(request):
    if request.method == "POST":
        messages.success(request, "Parcel received successfully.")
        return redirect("agents:parcel_list")
    return render(request, "agents/parcel_receive.html")


# ================================================================
# SHOPS
# ================================================================
@login_required(login_url="login")
def shops(request):
    all_shops = Shop.objects.all()
    return render(request, "agents/shops.html", {"shops": all_shops})


# ================================================================
# EMAIL / TEST EMAIL
# ================================================================
def test_email(request):
    context = {
        "user": request.user,
        "reset_link": "https://applemall.co.ke/reset/abc123"
    }
    send_custom_email(
        subject="Password Reset Request",
        message="You requested a password reset (fallback).",
        to_email="lihambomr@gmail.com",
        template_name="emails/password_reset_email.html",
        context=context
    )
    return render(request, "emails/sent.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Agent, Parcel

@login_required
def dashboard_view(request):
    user = request.user

    # Total agents (all agents)
    total_agents = Agent.objects.count()

    # Parcels stats
    total_parcels = Parcel.objects.count()
    received_parcels = Parcel.objects.filter(status='received').count()
    pending_parcels = Parcel.objects.filter(status='pending').count()

    # Agent-specific info
    referred_agents_count = 0
    commission_balance = 0

    if hasattr(user, 'agent'):
        # Now referred agents come from reverse FK: parent_agent__referred_agents
        referred_agents_count = user.agent.referred_agents.count()
        commission_balance = user.agent.commission_balance

    context = {
        'total_agents': total_agents,
        'total_parcels': total_parcels,
        'received_parcels': received_parcels,
        'pending_parcels': pending_parcels,
        'user': user,  # template uses user.agent.*
    }

    return render(request, 'agents/dashboard.html', context)

from django.shortcuts import render
from .models import Shop, Agent, Parcel

def shop_list(request):
    shops = Shop.objects.all()
    return render(request, 'agents/shop_list.html', {'shops': shops})

def agent_list(request):
    agents = Agent.objects.all()
    return render(request, 'agents/agent_list.html', {'agents': agents})

def parcel_list(request):
    parcels = Parcel.objects.all()
    return render(request, 'agents/parcel_list.html', {'parcels': parcels})
