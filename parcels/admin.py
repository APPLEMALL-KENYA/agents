# parcels/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import qrcode
import io
from .models import Parcel, Receipt
from .utils import send_custom_email  # Make sure this exists


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "customer_name",
        "destination",
        "status",
        "payment_status",
        "payment_method",
        "matatu_direct",
        "created_at",
    )
    list_filter = ("status", "payment_status", "payment_method", "matatu_direct")
    search_fields = ("reference", "customer_name", "destination", "customer_email")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Parcel Info", {
            "fields": (
                "reference",
                "customer_name",
                "customer_email",
                "destination",
                "origin_shop",
                "assigned_to",
                "matatu_direct",
                "dispatch_from",
                "dispatch_to",
            )
        }),
        ("Payment Details", {
            "fields": (
                "value_kes",
                "delivery_cost",
                "full_amount",
                "payment_status",
                "payment_method",
                "payment_type",
            )
        }),
        ("Status & Delivery Mode", {
            "fields": (
                "status",
                "via_matatu",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    actions = [
        "generate_receipt",
        "send_notification_email",
        "generate_delivery_note",
        "print_delivery_label",
        "mark_as_scanned",
    ]

    # --- 1. Generate Receipt/Invoice ---
    def generate_receipt(self, request, queryset):
        for parcel in queryset:
            receipt, created = Receipt.objects.get_or_create(
                parcel=parcel,
                defaults={
                    "amount": parcel.full_amount,
                    "payment_status": parcel.payment_status,
                }
            )
            if not created:
                receipt.amount = parcel.full_amount
                receipt.payment_status = parcel.payment_status
                receipt.save()
        self.message_user(request, "Receipt(s) generated/updated successfully.")
    generate_receipt.short_description = "Generate or Update Receipt for selected Parcels"

    # --- 2. Send Notification Email ---
    def send_notification_email(self, request, queryset):
        for parcel in queryset:
            subject = f"Parcel Update - {parcel.reference}"
            message = f"""
            Dear {parcel.customer_name},

            Your parcel with reference {parcel.reference} is currently marked as:
            Status: {parcel.status}
            Payment: {parcel.payment_status}

            Thank you for choosing DropAgent.
            """
            if parcel.customer_email:
                send_custom_email(subject, message, [parcel.customer_email])
        self.message_user(request, "Notification emails sent successfully.")
    send_notification_email.short_description = "Send Email Notification to Customers"

    # --- 3. Generate Delivery Note with QR Code ---
    def generate_delivery_note(self, request, queryset):
        parcel = queryset.first()
        if not parcel:
            self.message_user(request, "No parcel selected.")
            return

        qr_content = f"REF:{parcel.reference}|STATUS:{parcel.status}"
        qr = qrcode.make(qr_content)
        buffer = io.BytesIO()
        qr.save(buffer, "PNG")
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="image/png")
        response["Content-Disposition"] = f'attachment; filename="delivery_note_{parcel.reference}.png"'
        return response
    generate_delivery_note.short_description = "Generate Delivery Note with QR Code"

    # --- 4. Print Delivery Label (QR + Customer Info) ---
    def print_delivery_label(self, request, queryset):
        parcel = queryset.first()
        if not parcel:
            self.message_user(request, "No parcel selected.")
            return

        # QR Code
        qr_content = f"REF:{parcel.reference}|STATUS:{parcel.status}"
        qr = qrcode.make(qr_content)
        qr_buffer = io.BytesIO()
        qr.save(qr_buffer, "PNG")
        qr_buffer.seek(0)

        # Build label HTML (can print directly from browser)
        html_content = f"""
        <html>
            <body>
                <h2>Parcel Delivery Label</h2>
                <p><b>Reference:</b> {parcel.reference}</p>
                <p><b>Customer:</b> {parcel.customer_name}</p>
                <p><b>Destination:</b> {parcel.destination}</p>
                <img src="data:image/png;base64,{qr_buffer.getvalue().hex()}">
            </body>
        </html>
        """
        return HttpResponse(html_content)
    print_delivery_label.short_description = "Print Delivery Label (QR + Info)"

    def mark_as_scanned(self, request, queryset):
        for parcel in queryset:
            parcel.status = "IN_TRANSIT"
            parcel.save()
        self.message_user(request, "Selected parcel(s) marked as scanned and updated.")

    mark_as_scanned.short_description = "Mark selected parcels as Scanned"


# --- Receipt Admin ---
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("parcel", "amount", "payment_status", "issued_at")
    list_filter = ("payment_status",)
    search_fields = ("parcel__reference", "parcel__customer_name")
    readonly_fields = ("issued_at", "updated_at")  # Make sure `updated_at` exists in Receipt model
