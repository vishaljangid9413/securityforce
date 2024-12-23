from django.urls import path
from .views import zipcodeLookup

urlpatterns = [
    path('api/zipcodeLookup/<int:location>/', zipcodeLookup.as_view(), name='zipcode-lookup'),
    path('api/zipcodeLookup/', zipcodeLookup.as_view(), name='zipcode-lookup'),
]
