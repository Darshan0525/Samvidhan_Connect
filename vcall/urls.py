from django.contrib import admin
from django.urls import path,include
from vcall.views import *

urlpatterns = [
    path('',home_page),
    path('meeting/',video_call),
]