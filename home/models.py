# models.py
from django.db import models
from authentication.models import users
from django.contrib.auth.models import User
import random 
# Lawyer Profile Model
class LawyerProfile(models.Model):
    user = models.OneToOneField(users, on_delete=models.CASCADE, related_name='lawyer_profile')
    description = models.TextField(blank=True, null=True)
    speciality = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    profile_picture = models.ImageField(upload_to='lawyer_pictures/',default='default.jpg')
    experience_years = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=True)
    address=models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.user.user.username} - Lawyer Profile"

# Client Profile Model
class ClientProfile(models.Model):
    user = models.OneToOneField(users, on_delete=models.CASCADE, related_name='client_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='client_pictures/', default='default.jpg' )
   
    def __str__(self):
        return f"{self.user.user.username} - Client Profile"

# AppointmentSlot Model
class AppointmentSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
    ]
    
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'users__role': 'lawyer'})
    specialization = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    meet_id = models.PositiveIntegerField(unique=True, blank=True, null=True)  # Match Zego Cloud's `roomID`

    def save(self, *args, **kwargs):
        if not self.meet_id:  # Generate meet_id only if it doesn't exist
            self.meet_id = random.randint(1000, 9999)  # Random 4-digit number
        super().save(*args, **kwargs)

class BookedAppointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booked_appointments")
    slot = models.OneToOneField(AppointmentSlot, on_delete=models.CASCADE, related_name="booking")

    def __str__(self):
        return f"{self.client.username} booked {self.slot}"