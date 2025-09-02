# riders/views.py
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string

from parcels.models import Parcel, Invoice, DeliveryNote
from .models import RiderProfile, RiderWallet, RiderNotification

from xhtml2pdf import pisa  # PDF generation

# -------------------------
# Superadmin checks
# -------------------------
def is_superadmin(user):
    return user.is_superuser

@user_passes_test(is_superadmin)
def rider_dashboard_admin(request):
    """Superadmin view: list all riders"""
    riders = RiderProfile.objects.all()
    return render(request, 'riders/dashboard.html', {'riders': riders})

@user_passes_test(is_superadmin)
def suspend_rider(request, rider_id):
    rider = get_object_or_404(RiderProfile, id=rider_id)
    rider.status = 'SUSPENDED'
    rider.save()
    messages.success(request, f"Rider {rider.user.username} suspended.")
    return redirect('rider_dashboard_admin')

@user_passes_test(is_superadmin)
def edit_rider(request, rider_id):
    rider = get_object_or_404(RiderProfile, id=rider_id)
    if request.method == 'POST':
        rider.status = request.POST.get('status', rider.status)
        rider.phone = request.POST.get('phone', rider.phone)
        rider.save()
        messages.success(request, f"Rider {rider.user.username} updated.")
        return redirect('rider_dashboard_admin')
    return render(request, 'riders/edit_rider.html', {'rider': rider})

# -------------------------
# Rider dashboard
# -------------------------
@login_required
def rider_dashboard(request):
    try:
        rider = RiderProfile.objects.get(user=request.user)
    except RiderProfile.DoesNotExist:
        messages.error(request, "No rider profile found. Please register.")
        return redirect('register_rider')

    jobs = rider.job_set.filter(status__in=['ASSIGNED', 'IN_TRANSIT'])
    notifications = RiderNotification.objects.filter(rider=rider).order_by('-created_at')
    wallet, _ = RiderWallet.objects.get_or_create(rider=rider)

    return render(request, 'riders/rider_dashboard.html', {
        'rider': rider,
        'jobs': jobs,
        'notifications': notifications,
        'wallet': wallet,
    })

# -------------------------
# Pickup and delivery scans
# -------------------------
@login_required
def scan_pickup(request):
    """Rider scans parcel pickup"""
    if request.method == 'POST':
        reference = request.POST.get('reference')
        parcel = get_object_or_404(Parcel, reference=reference)
        parcel.current_status = 'IN_TRANSIT'
        parcel.save()
        messages.success(request, f"Parcel {parcel.reference} is now In Transit")
        return redirect('rider_dashboard')
    return render(request, 'riders/scan_pickup.html')

@login_required
def scan_delivery(request):
    """Rider scans parcel delivery"""
    if request.method == 'POST':
        reference = request.POST.get('reference')
        parcel = get_object_or_404(Parcel, reference=reference)
        action = request.POST.get('action')
        parcel.current_status = 'ARRIVED_PICKUP' if action == 'pickup_agent' else 'DELIVERED'
        parcel.save()
        messages.success(request, f"Parcel {parcel.reference} status updated to {parcel.current_status}")
        return redirect('rider_dashboard')
    return render(request, 'riders/scan_delivery.html')

# -------------------------
# Scan parcel, update status, earnings, PDFs
# -------------------------
@login_required
def scan_parcel(request, parcel_id=None):
    """Rider scans parcel, updates status, earnings, and generates PDFs."""
    rider = get_object_or_404(RiderProfile, user=request.user)

    # Determine parcel
    parcel = None
    if parcel_id:
        parcel = get_object_or_404(Parcel, id=parcel_id)
    elif request.method == "POST":
        reference = request.POST.get('reference')
        if reference:
            parcel = get_object_or_404(Parcel, reference=reference)

    if not parcel:
        messages.error(request, "No parcel specified.")
        return redirect('rider_dashboard')

    # Get related job
    job = get_object_or_404(rider.job_set, parcel=parcel)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "pickup":
            job.status = 'ARRIVED'
            job.save()
            RiderNotification.objects.create(rider=rider, message=f"Parcel {parcel.reference} picked up.")
            messages.success(request, f"Parcel {parcel.reference} picked up successfully.")

        elif action == "delivery":
            distance_str = request.POST.get('distance_km', '0')
            try:
                distance = Decimal(distance_str)
            except (InvalidOperation, TypeError):
                distance = Decimal('0')

            job.status = 'DELIVERED'
            job.save()

            wallet, _ = RiderWallet.objects.get_or_create(rider=rider)
            wallet.add_earning(distance)

            RiderNotification.objects.create(rider=rider, message=f"Parcel {parcel.reference} delivered.")
            messages.success(request, f"Parcel {parcel.reference} delivered successfully.")

        elif action == "receipt_pdf":
            return generate_pdf(
                'riders/receipt_pdf.html',
                {'parcel': parcel, 'rider': rider},
                f"Receipt_{parcel.reference}.pdf"
            )

        elif action == "delivery_note_pdf":
            return generate_pdf(
                'riders/delivery_note_pdf.html',
                {'parcel': parcel, 'rider': rider},
                f"DeliveryNote_{parcel.reference}.pdf"
            )

        return redirect('rider_dashboard')

    return render(request, 'riders/scan_parcel.html', {'job': job, 'parcel': parcel})

# -------------------------
# PDF helper
# -------------------------
def generate_pdf(template_src, context_dict, filename):
    """Generate PDF using xhtml2pdf."""
    html_string = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

# -------------------------
# Register rider
# -------------------------
@login_required
def register_rider(request):
    if RiderProfile.objects.filter(user=request.user).exists():
        messages.info(request, "You already have a rider profile.")
        return redirect('rider_dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        RiderProfile.objects.create(user=request.user, phone=phone, status='ACTIVE')
        messages.success(request, "Rider profile created successfully!")
        return redirect('rider_dashboard')

    return render(request, 'riders/register_rider.html')

# riders/views.py
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RiderProfile, RiderWallet

@login_required
def wallet_withdraw(request):
    """Allow rider to withdraw money from their wallet."""
    rider = get_object_or_404(RiderProfile, user=request.user)
    wallet, _ = RiderWallet.objects.get_or_create(rider=rider)

    if request.method == "POST":
        amount_str = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount_str)
            wallet.withdraw(amount)
            messages.success(request, f"Ksh {amount:.2f} withdrawn successfully!")
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount entered.")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('rider_dashboard')  # redirect after POST

    # GET request: render withdraw form
    return render(request, 'riders/wallet_withdraw.html', {'wallet': wallet})

from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .models import RiderWallet, RiderNotification

@login_required
def request_withdrawal(request):
    """Rider requests wallet withdrawal."""
    rider = request.user.riderprofile
    wallet, _ = RiderWallet.objects.get_or_create(rider=rider)

    if request.method == "POST":
        amount_str = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount_str)
            if amount > wallet.balance:
                messages.error(request, "Insufficient wallet balance.")
            else:
                RiderWallet.objects.create(wallet=wallet, amount=amount)
                messages.success(request, f"Withdrawal request of Ksh {amount} submitted for approval.")
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount entered.")

        return redirect('rider_dashboard')

    return render(request, 'riders/request_withdrawal.html', {'wallet': wallet})


# Superadmin approval view
@user_passes_test(lambda u: u.is_superuser)
def approve_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(RiderWallet, id=withdrawal_id)
    if withdrawal.status != 'PENDING':
        messages.error(request, "This withdrawal has already been processed.")
    else:
        try:
            withdrawal.approve(admin_user=request.user)
            messages.success(request, f"Withdrawal of Ksh {withdrawal.amount} approved successfully.")
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('superadmin_withdrawal_dashboard')

from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from .models import RiderWallet, RiderNotification, RiderProfile

@login_required
def withdraw_request(request):
    """Rider submits a withdrawal request."""
    rider = get_object_or_404(RiderProfile, user=request.user)
    wallet, _ = RiderWallet.objects.get_or_create(rider=rider)
    User = get_user_model()  # Use your custom user model

    if request.method == "POST":
        amount_str = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect('withdraw_request')

        try:
            # Use the withdraw method defined in RiderWallet
            wallet.withdraw(amount)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('withdraw_request')

        # Notify all superadmins
        superadmins = User.objects.filter(is_superuser=True)
        for admin in superadmins:
            RiderNotification.objects.create(
                rider=rider,  # optionally link to admin profile if needed
                message=f"Rider {rider.user.username} requested withdrawal of KSh {amount}."
            )

        messages.success(request, f"Withdrawal request for KSh {amount} submitted successfully.")
        return redirect('rider_dashboard')

    return render(request, 'riders/withdraw_request.html', {'wallet': wallet})

# riders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import RiderProfile, AvailableJob, Job
from decimal import Decimal

def available_jobs(request):
    rider = get_object_or_404(RiderProfile, user=request.user)
    jobs = AvailableJob.objects.all()
    return render(request, 'riders/available_jobs.html', {'jobs': jobs, 'rider': rider})

def bid_job(request, job_id):
    rider = get_object_or_404(RiderProfile, user=request.user)
    available_job = get_object_or_404(AvailableJob, id=job_id)

    if request.method == "POST":
        bid_amount_str = request.POST.get('bid_amount', available_job.min_bid_amount)
        bid_amount = Decimal(bid_amount_str)

        # Create Job and remove from AvailableJob
        Job.objects.create(
            parcel=available_job.parcel,
            rider=rider,
            bid_amount=bid_amount
        )
        available_job.delete()
        messages.success(request, f"You accepted job {available_job.parcel.reference} with KSh {bid_amount}")
        return redirect('ongoing_jobs')

    return render(request, 'riders/bid_job.html', {'job': available_job, 'rider': rider})

def ongoing_jobs(request):
    rider = get_object_or_404(RiderProfile, user=request.user)
    jobs = Job.objects.filter(rider=rider).exclude(status='DELIVERED')
    return render(request, 'riders/ongoing_jobs.html', {'jobs': jobs, 'rider': rider})
