from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from .utils import *
from django.utils.crypto import get_random_string
from django.db.models import Q
from home.models import LawyerProfile
# Create your views here.

def login_user(request):
    if request.method == "POST": 
        username_or_email = request.POST.get('email')  # Can be username or email
        password = request.POST.get('password')

        # Check if the input is a username or email
        user = User.objects.filter(Q(username=username_or_email) | Q(email=username_or_email)).first()

        if not user:
            messages.error(request, 'Invalid Username or Email')
            return redirect('/auth/login')

        # Authenticate with username (Django's `authenticate` doesn't support email by default)
        user = authenticate(username=user.username, password=password)
        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/auth/login')
        else:
            login(request, user)
            return redirect('/')  # Redirect to the home page after successful login

    return render(request, 'login.html')

def register_user(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('user_name')  
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Check if email or username is already registered
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Username or Email already exists.')
            return redirect('/auth/register')

        # Generate OTP and save in TempUser
        otp = generate_otp()
        temp_user = TempUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            otp=otp,
            role=role,
        )

        # Send OTP to user's email
        if send_email_otp(email, otp):
            return redirect(f'/auth/verify/{temp_user.id}/')  # Redirect to verification page
        else:
            temp_user.delete()
            messages.error(request, 'Failed to send OTP. Please try again.')
            return redirect('/auth/register')

    return render(request, 'register.html')


def verify_user(request, user_id):
    try:
        temp_user = TempUser.objects.get(id=user_id)
    except TempUser.DoesNotExist:
        messages.error(request, 'Invalid user or verification session expired.')
        return redirect('/auth/register')

    if request.method == "POST":
        otp = request.POST.get('otp')

        if temp_user.is_otp_valid() and temp_user.otp == otp:
            # Create the actual User
            user = User.objects.create(
                first_name=temp_user.first_name,
                last_name=temp_user.last_name,
                username=temp_user.username,
                email=temp_user.email,
            )
            user.set_password(temp_user.password)
            user.save()
            user_instance=users.objects.create(user=user, role=temp_user.role)
            # Delete TempUser
            if temp_user.role == 'lawyer':
                lawyer_profile = LawyerProfile.objects.get(user=user_instance)
                lawyer_profile.speciality = temp_user.specialization
                lawyer_profile.experience_years = temp_user.experience_years
                lawyer_profile.save()
            temp_user.delete()

            messages.success(request, 'Account verified successfully. You can log in now.')
            return redirect('/auth/login')
        else:
            messages.error(request, 'Invalid or expired OTP.')
            return redirect(f'/auth/verify/{user_id}/')

    return render(request, 'verify.html', {'user_id': user_id})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        # Check if email exists in User
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "No user found with this email address.")
            return redirect('/auth/forgot-password')

        # Generate OTP and save in TempUser
        otp = generate_otp()
        temp_user, created = TempUser.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'otp_created_at': timezone.now()},
        )

        if forgot_email_otp(email,otp):
            return redirect(f'/auth/reset-password/{temp_user.id}/')  # Redirect to reset password page
        else:
            messages.error(request, "Failed to send OTP. Please try again.")
            return redirect('/auth/forgot-password')

    return render(request, 'forgot_password.html')

def reset_password(request, temp_user_id):
    try:
        temp_user = TempUser.objects.get(id=temp_user_id)
    except TempUser.DoesNotExist:
        messages.error(request, "Invalid or expired session.")
        return redirect('/auth/forgotpassword')

    if request.method == "POST":
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate OTP
        if not temp_user.is_otp_valid():
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('/auth/forgot-password')

        if temp_user.otp != otp:
            messages.error(request, "Invalid OTP.")
            return redirect(f'/auth/reset-password/{temp_user.id}/')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(f'/auth/reset-password/{temp_user.id}/')

        # Update User's password
        user = User.objects.get(email=temp_user.email)
        user.set_password(new_password)
        user.save()

        # Delete TempUser entry
        temp_user.delete()

        messages.success(request, "Password reset successfully. You can now log in.")
        return redirect('/auth/login')

    return render(request, 'reset_password.html', {'temp_user_id': temp_user_id})
   
def logout_user(request):
    logout(request)
    return redirect('/')

def home(request):
    return render(request,'base.html')

def register_useru(request):
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == 'client':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('user_name')  
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = form_type

            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, 'Username or Email already exists.')
                return redirect('/auth/register')

            # Generate OTP and save in TempUser
            otp = generate_otp()
            temp_user = TempUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                otp=otp,
                role=role,
            )

            # Send OTP to user's email
            if send_email_otp(email, otp):
                return redirect(f'/auth/verify/{temp_user.id}/')  # Redirect to verification page
            else:
                temp_user.delete()
                messages.error(request, 'Failed to send OTP. Please try again.')
                return redirect('/auth/register')   
        if form_type == 'lawyer':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('user_name')  
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = form_type
            specialization = request.POST.get('specialization')
            experience_years = request.POST.get('experience_years')

            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, 'Username or Email already exists.')
                return redirect('/auth/register')
            
            otp = generate_otp()
            temp_user = TempUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                otp=otp,
                role=role,
                specialization=specialization,
                experience_years=experience_years,
            )

            if send_email_otp(email, otp):
                return redirect(f'/auth/verify/{temp_user.id}/')  # Redirect to verification page
            else:
                temp_user.delete()
                messages.error(request, 'Failed to send OTP. Please try again.')
                return redirect('/auth/register')
    return render(request,'registeru.html')

def contact(request):
    return render(request,'contact.html')