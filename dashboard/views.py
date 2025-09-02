from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

# check if user is superuser
def superuser_required(user):
    return user.is_superuser

def superadmin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("superadmin_dashboard")
        else:
            messages.error(request, "Invalid credentials or not a super admin")
    return render(request, "dashboard/superadmin_login.html")

@user_passes_test(superuser_required)
def superadmin_dashboard(request):
    return render(request, "dashboard/superadmin_dashboard.html")

def superadmin_logout(request):
    logout(request)
    return redirect("superadmin_login")
