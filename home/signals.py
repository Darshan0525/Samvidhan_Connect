from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import users
from .models import LawyerProfile, ClientProfile

@receiver(post_save, sender=users)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'lawyer':
            LawyerProfile.objects.create(user=instance)
        elif instance.role == 'client':
            ClientProfile.objects.create(user=instance)
