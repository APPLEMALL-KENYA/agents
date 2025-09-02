# riders/admin.py
from django.contrib import admin
from .models import RiderProfile, Job, RiderRating

# RiderProfile admin
@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'rating', 'total_jobs')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('rating', 'total_jobs')  # superadmin cannot edit these manually

# Job admin
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'rider', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'rider')
    search_fields = ('parcel__reference', 'rider__user__username')
    readonly_fields = ('assigned_at', 'completed_at')

# RiderRating admin
@admin.register(RiderRating)
class RiderRatingAdmin(admin.ModelAdmin):
    list_display = ('rider', 'client', 'job', 'rating', 'created_at')
    list_filter = ('rating', 'rider')
    search_fields = ('rider__user__username', 'client__username', 'job__parcel__reference')
    readonly_fields = ('created_at',)
from decimal import Decimal
from django.contrib import admin, messages
from decimal import Decimal, InvalidOperation
from .models import RiderWallet, RiderNotification, RiderProfile

@admin.register(RiderWallet)
class withdraw_requestAdmin(admin.ModelAdmin):
    list_display = ('rider', 'balance')
    actions = ['admin_withdraw']

    @admin.action(description="Withdraw from selected rider wallets")
    def admin_withdraw(self, request, queryset):
        """
        Admin can withdraw a specific amount from selected RiderWallets.
        Prompts are not possible in admin actions, so define a fixed amount for testing,
        or integrate a custom admin form for amount input.
        """
        # Example fixed amount for simplicity
        amount = Decimal('100.00')  # Replace with desired logic or form input

        success_count = 0
        for wallet in queryset:
            try:
                wallet.withdraw(amount)
                success_count += 1
            except ValueError as e:
                self.message_user(
                    request,
                    f"Failed to withdraw from {wallet.rider.user.username}: {e}",
                    level=messages.ERROR
                )
        self.message_user(
            request,
            f"Successfully processed withdrawals for {success_count} wallet(s)."
        )

@admin.register(RiderNotification)
class RiderNotificationAdmin(admin.ModelAdmin):
    list_display = ('rider', 'message', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('rider__user__username', 'message')
