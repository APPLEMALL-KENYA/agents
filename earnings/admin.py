from django.contrib import admin

# Register your models here.
from django.contrib import admin

from notifications.models import Notification
from .models import Earning  # adjust if your model name is different

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ("agent", "amount", "created_at")  # adjust fields to match your model
    search_fields = ("agent__user__username",)
    list_filter = ("created_at",)


