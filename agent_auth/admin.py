from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AgentUser

@admin.register(AgentUser)
class AgentUserAdmin(UserAdmin):
    # Include custom fields in admin form
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("phone", "address")}),
    )
