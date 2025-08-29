from django.contrib import admin
from .models import Shop, Agent, Parcel

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'phone', 'email', 'created_at', 'updated_at']
    search_fields = ['name', 'location', 'phone', 'email']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'reference_code', 'is_shop', 'commission_balance']
    list_filter = ['is_shop']
    search_fields = ['name', 'reference_code', 'email', 'phone']

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['id', 'tracking_code', 'shop', 'agent', 'sender_name', 'receiver_name', 'receiver_phone', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'shop', 'agent']
    search_fields = ['tracking_code', 'sender_name', 'receiver_name', 'receiver_phone']
