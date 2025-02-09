from django.urls import path
from . import views  # Make sure this import is correct
from home.views import *

urlpatterns = [
    path('', views.home_page, name='home_page'),  # Correct usage
    path('client_d/', views.client_d, name='client_d'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('schedule-appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('delete-appointment-slot/<int:slot_id>/', views.delete_appointment_slot, name='delete_appointment_slot'),
    path('update-appointment-slot/<int:slot_id>/', views.update_appointment_slot, name='update_appointment_slot'),
    path('view-appointments/', views.view_appointments, name='view_appointments'),
    path('lawyer-appointments/', views.lawyer_appointments, name='lawyer_appointments'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-cancel/', payment_cancel, name='payment-cancel'),
    path('wikipedia/', wikipedia, name='wikipedia'),
    path('sidebar/', sidebar, name='sidebar'),
    path('learn_more/', learn_more, name='learn_more'),
    path('vl_profile/<str:username>/',vl_profile,name='Viewlaweyerp'),
    path('payment-successful/', payment_successful_view, name='payment_successful')
    
]
