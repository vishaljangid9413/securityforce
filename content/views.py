from rest_framework import generics
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import FAQ
from .serializers import FAQSerializer
from rest_framework.response import Response

class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'question']  # Specify fields you want to allow filtering on

class FAQView(APIView):
     def get(self, request, format=None):
        queryset = FAQ.objects.all().distinct('category').values('category').order_by('category')        
        return Response([d['category'] for d in queryset])
