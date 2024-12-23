from rest_framework.views import APIView
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import *
from .serializers import *
from django.db import transaction
# from .filters import ReportFilter 
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


# class ReportListCreateAPIView(APIView):
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
#     filterset_class = ReportFilter

#     def get(self, request, format=None):
#         reports = Report.objects.all()
#         serializer = ReportSerializer(reports, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = ReportSerializer(data=request.data)
#         if serializer.is_valid():
#             report = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ReportDetailAPIView(APIView):
#     def get_object(self, pk):
#         try:
#             return Report.objects.get(pk=pk)
#         except Report.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         report = self.get_object(pk)
#         serializer = ReportSerializer(report)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         report = self.get_object(pk)
#         serializer = ReportSerializer(report, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk, format=None):
#         report = self.get_object(pk)
#         serializer = ReportSerializer(report, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         report = self.get_object(pk)
#         report.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# ** FEEDS LIST API **



# ** FIELD OFFICER FEEDS API **
class FeedView(APIView):
    
    def get(self, request, user_id=None, format=None):
        if user_id:
            try:
                user = User.objects.get(pk=user_id)            
            except:
                return Response({'detail':"Enter a valid User Id"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        feeds = Feed.objects.filter(user__id = user.id)
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)
        
    def post(self, request, format=None):
        serializer = FeedPostSerializer(data=request.data, context={"user":request.user.id})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Feed Submited successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ** COMPLAINT LIST API **
class ComplaintListView(generics.ListAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'message', 'checkpoint')
    search_fields = ('user', 'message', 'checkpoint')
    
    
# ** COMPLAINT API ** 
class ComplaintView(APIView):
    
    def get(self, request, user_id=None, format = None):
        if user_id:
            try:
                user = User.objects.get(pk=user_id)            
            except:
                return Response({'detail':"Enter a valid User Id"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        complaints = Complaint.objects.filter(user__id = user.id)
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ComplaintPostSerializer(data=request.data, context={"user":request.user.id})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Complaint Submited successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ** SOS LIST API **
class SOSListView(generics.ListAPIView):
    queryset = SOS.objects.all()
    serializer_class = SOSSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'message', 'checkpoint')
    search_fields = ('user', 'message', 'checkpoint')
    
    
# ** SOS API **
class SOSView(APIView):
    
    def get(self, request, user_id=None, format = None):
        if user_id:
            try:
                user = User.objects.get(pk=user_id)            
            except:
                return Response({'detail':"Enter a valid User Id"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        sos = SOS.objects.filter(user__id = user.id)
        serializer = SOSSerializer(sos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SOSPostSerializer(data=request.data, context={"user":request.user.id})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'SOS Submited successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ** REPORT List API ** 
class ReportView(generics.ListAPIView):
    queryset = Feed.objects.all()    
    serializer_class = FeedSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'checkpoint',) 
    search_fields = ('user',)
    
    
    
    