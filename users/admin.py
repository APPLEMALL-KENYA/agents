from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, AgentProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
 list_display = ("username", "email", "role", "is_active")
 list_filter = ("role", "is_active")
 search_fields = ("username", "email")


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
 list_display = ("user", "phone", "location", "parent", "is_active")
 list_filter = ("is_active",)
 search_fields = ("user__username", "phone", "location")