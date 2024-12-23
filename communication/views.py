from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from .models import Message, Newsletter, Notification, Scheduler, MessageToUser, NewsletterToUser, NotificationToUser, HelpQues
from .serializers import (MessageSerializer, MessageToUserPostSerializer, MessageToUserSerializer, NewsletterSerializer, NewsletterToUserPostSerializer, NewsletterToUserPostSerializer, NotificationSerializer, NotificationToUserSerializer, NotificationToUserPostSerializer, SchedulerSerializer,  NotificationToUserSerializer, NewsletterToUserSerializer, HelpQuesSerializer)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from business.permissions import IsBusinessAdmin, IsFieldOfficer, IsManager
from accounts.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics


# ** MESSAGE LIST API **
class MessageListView(generics.ListAPIView):
    queryset = MessageToUser.objects.all()
    serializer_class = MessageToUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('message', 'sender', 'reciever', 'is_read')
    search_fields = ('message', 'sender', 'reciever', 'is_read')


# ** MESSAGE API **
class MessageView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin | IsManager | IsFieldOfficer)]

    def get(self, request, format=None):
        user_id = request.user.id
        try:
            sent_data = MessageToUser.objects.filter(sender=user_id)
            sent_serializer = MessageToUserSerializer(sent_data, many=True)

            recieved_data = MessageToUser.objects.filter(reciever=user_id)
            recieved_serializer = MessageToUserSerializer(recieved_data, many=True)

            data = {
                'sent_messages':sent_serializer.data,
                'recieved_messages': recieved_serializer.data
            }
            return Response(data)
        except Exception as e:
            return Response({'detail':e})
            
    def post(self, request, format=None):
        serializer = MessageToUserPostSerializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Message Sent successfully'}, status=status.HTTP_201_CREATED)
        else:   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, message_id, format=None):
        user_id = request.user.id
        try:
            messages_to_user = MessageToUser.objects.filter(sender__id = user_id, message__id = message_id)
            
        except Exception as e:
            return Response({'detail':e})
        
        messages = Message.objects.filter(pk = message_id)
        for obj in messages:
            serializer = MessageSerializer(obj, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Message Updated Successfully'})
        return Response(serializer.errors)

    def delete(self, request, message_id, format=None):
        user_id = request.user.id
        try:
            message_to_user = MessageToUser.objects.filter(sender__id = user_id, message__id = message_id).first()
            message_to_user.message.delete()
            return Response({'detai':"Message Deleted Successfully"})
        except:
            return Response({'detail':'Enter a valid data'}, status = status.HTTP_404_NOT_FOUND)


# ** NEWSLETTER LIST API **
class NewsletterListView(generics.ListAPIView):
    queryset = NewsletterToUser.objects.all()
    serializer_class = NewsletterToUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('newsletter', 'sender', 'reciever', 'is_read')
    search_fields = ('newsletter', 'sender', 'reciever', 'is_read')


# ** NEWSLETTER API **
class NewsletterView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]

    def get(self, request, format=None):
        user_id = request.user.id
        try:
            sent_data = NewsletterToUser.objects.filter(sender=user_id)
            serializer = NewsletterToUserSerializer(sent_data, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})
            
    def post(self, request, format=None):
        serializer = NewsletterToUserPostSerializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Newsletter Sent successfully'}, status=status.HTTP_201_CREATED)
        else:   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, newsletter_id, format=None):
        user_id = request.user.id
        try:
            newsletter_to_user = NewsletterToUser.objects.filter(sender__id = user_id, newsletter__id = newsletter_id)
        except Exception as e:
            return Response({'detail':e})
        
        newsletters = Newsletter.objects.filter(pk = newsletter_id)
        for obj in newsletters:
            serializer = NewsletterSerializer(obj, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Newsletter Updated Successfully'})
        return Response(serializer.errors)

    def delete(self, request, newsletter_id, format=None):
        user_id = request.user.id
        try:
            newsletter_to_user = NewsletterToUser.objects.filter(sender__id = user_id, newsletter__id = newsletter_id).first()
            newsletter_to_user.newsletter.delete()
            return Response({'detai':"Newsletter Deleted Successfully"})
        except:
            return Response({'detail':'Enter a valid data'}, status = status.HTTP_404_NOT_FOUND)


# ** NOTIFICATION LIST API **
class NotificationListView(generics.ListAPIView):
    queryset = NotificationToUser.objects.all()
    serializer_class = NotificationToUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('notification', 'sender', 'reciever', 'is_read')
    search_fields = ('notification', 'sender', 'reciever', 'is_read')


# ** NEWSLETTER API **
class NotificationView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]

    def get(self, request, format=None):
        user_id = request.user.id
        try:
            sent_data = NotificationToUser.objects.filter(sender=user_id)
            serializer = NotificationToUserSerializer(sent_data, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})
            
    def post(self, request, format=None):
        serializer = NotificationToUserPostSerializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Notification Sent successfully'}, status=status.HTTP_201_CREATED)
        else:   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, notification_id, format=None):
        user_id = request.user.id
        try:
            notification_to_user = NotificationToUser.objects.filter(sender__id = user_id, notification__id = notification_id)
        except Exception as e:
            return Response({'detail':e})
        
        notifications = Notification.objects.filter(pk = notification_id)
        for obj in notifications:
            serializer = NotificationSerializer(obj, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Notification Updated Successfully'})
        return Response(serializer.errors)

    def delete(self, request, notification_id, format=None):
        user_id = request.user.id
        try:
            notification_to_user = NotificationToUser.objects.filter(sender__id = user_id, notification__id = notification_id).first()
            notification_to_user.notification.delete()
            return Response({'detai':"Notification Deleted Successfully"})
        except:
            return Response({'detail':'Enter a valid data'}, status = status.HTTP_404_NOT_FOUND)


# ** HELP QUES AND ANSWER LIST API **
class HelpQuesListView(generics.ListAPIView):
    queryset = HelpQues.objects.all()
    serializer_class = HelpQuesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'question')
    search_fields = ('category', 'question')


# ** HELP QUES AND ANSWER API **
class HelpQuesView(APIView):
    
    def get(self, request, format = None):
        try:
            obj = HelpQues.objects.all()
            serializer = HelpQuesSerializer(obj, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})


class MessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsBusinessAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsBusinessAdmin]  


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsBusinessAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NewsletterDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsBusinessAdmin]


class NotificationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsBusinessAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsBusinessAdmin]


class SchedulerListCreateView(generics.ListCreateAPIView):
    queryset = Scheduler.objects.all()
    serializer_class = SchedulerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sender = self.request.user
        recipients = serializer.validated_data.get('recipients')
        
        # Check if the sender is a Business Admin and the recipients are related to the same business
        if sender.business.is_admin(sender) and all([sender.business == recipient.business for recipient in recipients.all()]):
            serializer.save(sender=sender)
        # Check if the sender is a superuser or staff
        elif sender.is_superuser or sender.is_staff:
            serializer.save(sender=sender)
        else:
            # Raise an error if the user does not have permission
            raise PermissionDenied("You do not have permission to send scheduled messages to these recipients.")


class SchedulerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scheduler.objects.all()
    serializer_class = SchedulerSerializer
    permission_classes = [permissions.IsAuthenticated]
