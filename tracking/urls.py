from django.urls import path
from .views import GPSDataListCreateAPIView, GPSDataDetailAPIView

urlpatterns = [
    path('api/gpsdata/', GPSDataListCreateAPIView.as_view(), name='gpsdata-list'),
    path('api/gpsdata/<int:pk>/', GPSDataDetailAPIView.as_view(), name='gpsdata-detail'),
]
'''
POST /gpsdata/ for creating GPS data.
GET /gpsdata/ for listing all GPS data.
GET /gpsdata/<pk>/ for retrieving a specific GPS data.
PUT /gpsdata/<pk>/ for updating a specific GPS data.
PATCH /gpsdata/<pk>/ for partially updating a specific GPS data.
DELETE /gpsdata/<pk>/ for deleting a specific GPS data.
'''