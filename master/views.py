from django.shortcuts import render
from .models import HelpCategory, Shift
from .serializers import HelpCategorySerializer, ShiftMasterSerializer
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response

# ** SHIFT MASTER API **
class ShiftView(APIView):

    def get(self, request, format = None):
        try:
            obj = Shift.objects.all()
            serializer = ShiftMasterSerializer(obj, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})

# ** HELP CATEGORY API **
class HelpCategoryView(APIView):
    
    def get(self, request, format = None):
        try:
            obj = HelpCategory.objects.all()
            serializer = HelpCategorySerializer(obj, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})
        