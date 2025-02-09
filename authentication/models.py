from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class users(models.Model):
    ROLE_CHOICES = [
        ('lawyer', 'lawyer'),
        ('client', 'client'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class TempUser(models.Model):
    ROLE_CHOICES = [
        ('lawyer', 'Lawyer'),
        ('client', 'Client'),
    ]
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, blank=True, null=True)  # Store hashed passwords for safety
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')  # Add role field
    specialization = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)

    def is_otp_valid(self):
        """Check if the OTP is valid (e.g., within 10 minutes)."""
        expiration_time = self.otp_created_at + timedelta(minutes=10)
        return timezone.now() <= expiration_time

    def __str__(self):
        return f"Temporary User {self.username} - {self.role}"
