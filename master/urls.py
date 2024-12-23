from django.urls import path
from .views import *

urlpatterns = [
    path('api/shifts/', ShiftView.as_view(), name='shifts'),
]
