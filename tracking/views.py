from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import GPSData
from .serializers import GPSDataSerializer

class GPSDataListCreateAPIView(ListCreateAPIView):
    serializer_class = GPSDataSerializer
    queryset = GPSData.objects.all()

class GPSDataDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = GPSDataSerializer
    queryset = GPSData.objects.all()
