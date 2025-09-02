from django.contrib import admin

# Register your models here.
# shops/admin.py
from django.contrib import admin
from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
 list_display = ("name", "contact_phone", "latitude", "longitude")
 search_fields = ("name", "contact_phone")