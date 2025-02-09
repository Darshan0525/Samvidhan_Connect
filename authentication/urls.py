from django.contrib import admin
from django.urls import path,include
from authentication.views import *
urlpatterns = [
    path('login/',login_user, name='login'),
    path('register/',register_useru,name='register'),
    path('logout/',logout_user),
    path('',home),
    path('verify/<int:user_id>/', verify_user, name='verify_user'),
    path('forgot-password/',forgot_password,name='forgot_password'),
    path('reset-password/<int:temp_user_id>/',reset_password,name='reset_password'),
    path('contact/',contact,name='contact'),
]