# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic 
from .models import AppointmentSlot, ClientProfile, LawyerProfile,BookedAppointment 
from authentication.models import users
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import AppointmentSlotForm,LawyerProfileForm, ClientProfileForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm

def home_page(request):
    if request.user.is_authenticated:
        # Logic for authenticated users
        user = get_object_or_404(users, user__username=request.user.username)
        if user.role == 'lawyer':
            profile = get_object_or_404(LawyerProfile, user=user)
        elif user.role == 'client':
            profile = get_object_or_404(ClientProfile, user=user)
        else:
            profile = None
        return render(request, 'base_home.html',{'profile':profile})
    else:
        # Redirect or render logic for unauthenticated users
        return redirect('/auth/')
    
def sidebar(request):
    if request.user.is_authenticated:
        # Logic for authenticated users
        user = get_object_or_404(users, user__username=request.user.username)
        if user.role == 'lawyer':
            profile = get_object_or_404(LawyerProfile, user=user)
        elif user.role == 'client':
            profile = get_object_or_404(ClientProfile, user=user)
        else:
            profile = None
        return render(request, 'sidebar.html',{'profile':profile})
    else:
        # Redirect or render logic for unauthenticated users
        return redirect('/auth/')

def view_profile(request, username):
    # Fetch the User instance associated with the username
    user = get_object_or_404(users, user__username=username)

    # Determine if the user is a lawyer or client
    if user.role == 'lawyer':
        profile = get_object_or_404(LawyerProfile, user=user)
    elif user.role == 'client':
        profile = get_object_or_404(ClientProfile, user=user)
    else:
        profile = None

    return render(request, 'profile.html', {'profile': profile})

def edit_profile(request):
    # Get the extended user model
    extended_user = get_object_or_404(users, user=request.user)
    
    if extended_user.role == 'lawyer':
        profile = get_object_or_404(LawyerProfile, user=extended_user)
        form_class = LawyerProfileForm
    elif extended_user.role == 'client':
        profile = get_object_or_404(ClientProfile, user=extended_user)
        form_class = ClientProfileForm
    else:
        return HttpResponse("Invalid role", status=400)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited Successfully')
            return redirect('view_profile', username=request.user.username)
    else:
        form = form_class(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

def vl_profile(request,username):
    userd = get_object_or_404(users, user__username=username)
    profile = get_object_or_404(LawyerProfile, user=userd)

    return render(request,'vl_profile.html',{'profile':profile})

# Function to convert time to AM/PM format
def time_to_ampm(time_obj):
    # Format time and handle '12:00 PM' to show only '12'
    formatted_time = time_obj.strftime('%I:%M %p')
    # If it's '12:00 PM', convert it to '12'
    if formatted_time.startswith("12:00 PM"):
        return "12"
    return formatted_time  # This will return time in 12-hour format (AM/PM)


# View to schedule appointment (only accessible by lawyers)
def schedule_appointment(request):
    if request.user.users.role != 'lawyer':
        return redirect('home_page')  # Redirect non-lawyer users to home or an appropriate page
    
    lawyer = request.user
    # Fetch the lawyer's scheduled time slots
    appointment_slots = AppointmentSlot.objects.filter(lawyer=lawyer)

    # Convert times to AM/PM format
    formatted_slots = []
    for slot in appointment_slots:
        formatted_slots.append({
            'id': slot.id,
            'specialization': slot.specialization,
            'date': slot.date,
            'start_time': time_to_ampm(slot.start_time),
            'end_time': time_to_ampm(slot.end_time),
            'amount':slot.amount,
            'status': slot.status
        })

    if request.method == 'POST':
        form = AppointmentSlotForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.lawyer = request.user  # Link the appointment to the logged-in lawyer
            appointment.save()
            messages.success(request, 'Your appointment slot has been successfully scheduled.')
            return redirect('schedule_appointment')  # Redirect to the home page after scheduling
    else:
        form = AppointmentSlotForm()

    return render(request, 'lawyer_d.html', {'form': form, 'appointment_slots': formatted_slots})

# Delete the appointment slot
@login_required
def delete_appointment_slot(request, slot_id):
    try:
        slot = AppointmentSlot.objects.get(id=slot_id, lawyer=request.user)
        slot.delete()
        messages.success(request, 'The appointment slot has been successfully deleted.')
    except AppointmentSlot.DoesNotExist:
        messages.error(request, 'The appointment slot does not exist or is not yours.')
    
    return redirect('lawyer_appointments')

# Update the appointment slot
@login_required
def update_appointment_slot(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id, lawyer=request.user)
    
    if request.method == 'POST':
        form = AppointmentSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, 'The appointment slot has been successfully updated.')
            return redirect('lawyer_appointments')
    else:
        form = AppointmentSlotForm(instance=slot)

    return render(request, 'update_appointment_slot.html', {'form': form})

@login_required
def client_d(request):
    # Ensure only clients access this view
    if request.user.users.role != 'client':
        return redirect('home_page')

    # Fetch all available slots
    available_slots = AppointmentSlot.objects.filter(status='available')

    # Filter by specialization (if query exists)
    specialization_query = request.GET.get('specialization', '')
    if specialization_query:
        available_slots = available_slots.filter(specialization__icontains=specialization_query)

    # Prepare data for template
    slots_with_profiles = []
    for slot in available_slots:
        # Get the lawyer's profile picture
        lawyer_users_instance = get_object_or_404(users, user=slot.lawyer)
        lawyer_profile = get_object_or_404(LawyerProfile, user=lawyer_users_instance)
        slots_with_profiles.append({
            'slot': slot,
            'profile_picture': lawyer_profile.profile_picture.url,
        })

    # Handle slot booking
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        slot = get_object_or_404(AppointmentSlot, id=slot_id, status='available')

        # Create a booked appointment entry
        BookedAppointment.objects.create(client=request.user, slot=slot)

        # Update slot status to "booked"
        slot.status = 'booked'
        slot.save()

        # Get the lawyer and client details
        client = request.user
        lawyer = slot.lawyer  # Get the `User` instance for the lawyer
        lawyer_users_instance = get_object_or_404(users, user=lawyer)  # Fetch `users` instance
        lawyer_profile = get_object_or_404(LawyerProfile, user=lawyer_users_instance)  # Fetch LawyerProfile
        profile_picture = lawyer_profile.profile_picture.url  # Get the profile picture URL

        # Redirect after success
        return redirect(reverse('client_d'))

    # Render the template
    return render(request, 'client_d.html', {
        'slots_with_profiles': slots_with_profiles,
    })


@login_required
def view_appointments(request):
    # Fetch booked appointments for the logged-in user
    booked_appointments = BookedAppointment.objects.filter(client=request.user).select_related('slot', 'slot__lawyer')
    
    # Prepare data for the template
    appointments_with_profiles = []
    for appointment in booked_appointments:
        # Get the lawyer's profile picture
        lawyer_users_instance = get_object_or_404(users, user=appointment.slot.lawyer)
        lawyer_profile = get_object_or_404(LawyerProfile, user=lawyer_users_instance)
        
        # Append the appointment and profile picture to the list
        appointments_with_profiles.append({
            'appointment': appointment,
            'profile_picture': lawyer_profile.profile_picture.url,
        })
    
    # Pass the appointments with profiles to the template
    context = {
        'appointments_with_profiles': appointments_with_profiles,
    }
    return render(request, 'view_appointments.html', context)



def lawyer_appointments(request):
    # Filter slots based on status
    available_slots = AppointmentSlot.objects.filter(lawyer=request.user, status='available')
    booked_slots = AppointmentSlot.objects.filter(lawyer=request.user, status='booked')
    
    return render(request, 'lawyer_appointment.html', {
        'available_slots': available_slots,
        'booked_slots': booked_slots,
    })


#payments
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

from django.views import View


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        slot_id = request.POST.get('slot_id')
        slot = get_object_or_404(AppointmentSlot, id=slot_id, status='available')
        host = request.get_host()

        try:
            # Create the Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': f"Appointment with {slot.lawyer.username}",
                                'description': f"Specialization: {slot.specialization}, Date: {slot.date}",
                            },
                            'unit_amount': int(slot.amount * 100),  # Convert to paise
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"http://{host}{reverse('payment-success')}?slot_id={slot.id}",
                cancel_url=f"http://{host}{reverse('payment-cancel')}",
                customer_creation='always',  # Ensure a customer is created
                billing_address_collection='required',  # Request billing address
                shipping_address_collection={
                    'allowed_countries': ['IN'],  # Collect shipping addresses from India
                }
            )
            return redirect(checkout_session.url, code=303)
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {e.user_message}")
            return redirect('client_d')  # Redirect back to the slot listing page


def payment_success(request):
    slot_id = request.GET.get('slot_id')
    slot = get_object_or_404(AppointmentSlot, id=slot_id, status='available')

    # Mark the slot as booked
    slot.status = 'booked'
    slot.save()

    # Create a booked appointment entry
    BookedAppointment.objects.create(client=request.user, slot=slot)

    # Send email notifications
    client = request.user
    lawyer = slot.lawyer
    try:
        send_mail(
            'Appointment Booking Confirmation',
            f'Dear {client.username},\n\nYour appointment with lawyer {lawyer.username} on {slot.date} from {slot.start_time} to {slot.end_time} has been confirmed and the payment of ₹{slot.amount} has been successful.',
            settings.DEFAULT_FROM_EMAIL,
            [client.email],
            fail_silently=False,
        )
        send_mail(
            'New Appointment Booked',
            f'Dear {lawyer.username},\n\nA new appointment has been booked by {client.username} on {slot.date} from {slot.start_time} to {slot.end_time}. The payment of ₹{slot.amount} has been received.',
            settings.DEFAULT_FROM_EMAIL,
            [lawyer.email],
            fail_silently=False,
        )
    except Exception as e:
        messages.error(request, f"An error occurred while sending email notifications: {str(e)}")

    return render(request, 's.html')


def payment_cancel(request):
    return render(request, 'confirmation.html', {'payment_status': 'cancel'})

# options

def wikipedia(request):
    return render(request, 'wikipedia.html')

def learn_more(request):
    return render(request, 'learn_more.html')

def payment_successful_view(request):
    # Pass the slot details to the template
    return render(request, 's.html')