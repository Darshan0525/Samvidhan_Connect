from django.contrib import admin
from .models import LawyerProfile,ClientProfile
# Register your models here.
admin.site.register(LawyerProfile)
admin.site.register(ClientProfile)