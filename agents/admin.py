from django.contrib import admin
from .models import Shop, Agent, Parcel

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'phone', 'email', 'created_at', 'updated_at']
    search_fields = ['name', 'location', 'phone', 'email']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'shop', 'phone', 'email', 'active', 'created_at']
    list_filter = ['active', 'shop']
    search_fields = ['name', 'phone', 'email', 'shop__name']

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['id', 'tracking_code', 'shop', 'agent', 'sender_name', 'receiver_name', 'receiver_phone', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'shop', 'agent']
    search_fields = ['tracking_code', 'sender_name', 'receiver_name', 'receiver_phone']
