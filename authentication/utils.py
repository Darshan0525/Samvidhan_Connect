import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_email_otp(email, otp):
    """Send an email with the OTP."""
    try:
        subject = 'Your OTP for Account Verification'
        message = f'Your OTP is {otp}. It will expire in 10 minutes.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        return False
    return True

def forgot_email_otp(email,otp):
    try:
        subject = 'Your OTP for password reset is'
        message = f'Your OTP is {otp}. It will expire in 10 minutes.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        return False
    return True
