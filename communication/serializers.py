from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Newsletter, Notification, Scheduler, MessageToUser, NewsletterToUser, NotificationToUser, HelpQues
from master.serializers import HelpCategorySerializer
from master.models import HelpCategory
from accounts.serializers import UserSerializer
from django.db import transaction
from master.serializers import UserMasterSerializer

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Message
        fields = '__all__'


class MessageToUserSerializer(serializers.ModelSerializer):
    message = MessageSerializer()
    sender = UserMasterSerializer()
    reciever = UserMasterSerializer()
    
    class Meta:
        model = MessageToUser
        fields = ('sender', 'reciever', 'message', 'is_read')


class MessageToUserPostSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    category = serializers.ChoiceField(choices=Message.CATEGORY_CHOICES) 
    
    receiver_id = serializers.JSONField()
    message_id = serializers.IntegerField(required=False)
    is_read = serializers.BooleanField(required=False)
    

    def create(self, validated_data):
        title = validated_data.get('title')
        content = validated_data.get('content')
        category = validated_data.get('category')

        receiver_id = validated_data.get('receiver_id')
        message_id = validated_data.get('message_id')
        is_read = validated_data.get('is_read')

        try:
            with transaction.atomic():
                sender = self.context['user']
                
                if message_id:
                    try:
                        message = Message.objects.get(id=message_id)
                    except:
                        raise Exception("Please enter a valid Message Id")
                else:
                    message = Message.objects.create(title=title, content=content, category=category)
                
                if receiver_id:
                    try:
                        users = [User.objects.get(id = receiver_id[str(id)]) for id in range(0, len(receiver_id))]
                        create_objs = [MessageToUser(reciever=users[index], sender=sender, message=message) for index in range(0, len(users))]
                        obj = MessageToUser.objects.bulk_create(create_objs)
                    except:
                        raise Exception("Please enter a valid User Id")
                
                return obj
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)


class NewsletterSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Newsletter
        fields = '__all__'


class NewsletterToUserSerializer(serializers.ModelSerializer):
    newsletter = NewsletterSerializer()
    sender = UserMasterSerializer()
    reciever = UserMasterSerializer()
    
    class Meta:
        model = NewsletterToUser
        fields = ('sender', 'reciever', 'newsletter', 'is_read')


class NewsletterToUserPostSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    content = serializers.CharField(required=False)
    is_html = serializers.BooleanField(required=False)
    html_content = serializers.CharField(required=False)
    image = serializers.FileField(required=False)
    video = serializers.FileField(required=False)
    
    receiver_id = serializers.CharField()
    newsletter_id = serializers.IntegerField(required=False)
    

    def create(self, validated_data):
        title = validated_data.get('title')
        url = validated_data.get('url')
        content = validated_data.get('content')
        is_html = validated_data.get('is_html')
        html_content = validated_data.get('html_content')
        image = validated_data.get('image')
        video = validated_data.get('video')

        receiver_id = validated_data.get('receiver_id')
        newsletter_id = validated_data.get('newsletter_id')


        try:
            with transaction.atomic():
                sender = self.context['user']
                
                if newsletter_id:
                    try:
                        newsletter = Newsletter.objects.get(id=newsletter_id)
                    except:
                        raise Exception("Please enter a valid Newsletter Id")
                else:
                    newsletter = Newsletter.objects.create(url=url, content=content, is_html=is_html, html_content=html_content, image=image, video = video, title=title)
                
                if receiver_id:
                    try:
                        receiver_ids = receiver_id.split(', ')
                        users = [User.objects.get(id = str(id)) for id in receiver_ids]
                        create_objs = [NewsletterToUser(reciever=user, sender=sender, newsletter=newsletter) for user in users]
                        obj = NewsletterToUser.objects.bulk_create(create_objs)
                    except:
                        raise Exception("Please enter a valid User Id")
                
                return 'obj'
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)


class NotificationSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationToUserSerializer(serializers.ModelSerializer):
    sender= UserMasterSerializer()
    reciever= UserMasterSerializer()
    notification = NotificationSerializer()

    class Meta:
        model = NotificationToUser
        fields = ('sender', 'reciever', 'notification', 'is_read')


class NotificationToUserPostSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    image = serializers.FileField(required=False)
    category = serializers.ChoiceField(choices=Notification.CATEGORY_CHOICES) 
    
    receiver_id = serializers.CharField()
    notification_id = serializers.IntegerField(required=False)
    is_read = serializers.BooleanField(required=False)
    

    def create(self, validated_data):
        title = validated_data.get('title')
        content = validated_data.get('content')
        image = validated_data.get('image')
        category = validated_data.get('category')

        receiver_id = validated_data.get('receiver_id')
        notification_id = validated_data.get('notification_id')
        is_read = validated_data.get('is_read')

        try:
            with transaction.atomic():
                sender = self.context['user']
                
                if notification_id:
                    try:
                        notification = Notification.objects.get(id=notification_id)
                    except:
                        raise Exception("Please enter a valid Notification Id")
                else:
                    notification = Notification.objects.create(content=content, image=image, category=category, title=title)
                        
                if receiver_id:
                    try:
                        receiver_ids = receiver_id.split(', ')
                        users = [User.objects.get(id = str(id)) for id in receiver_ids]
                        create_objs = [NotificationToUser(reciever=user, sender=sender, notification=notification) for user in users]
                        obj = NotificationToUser.objects.bulk_create(create_objs)
                    except:
                        raise Exception("Please enter a valid User Id")
                
                return 'obj'
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)


class HelpQuesSerializer(serializers.ModelSerializer):
    category = HelpCategorySerializer()
    
    class Meta:
        model = HelpQues
        fields = ('question', 'answer', 'date', 'time', 'category')


class SchedulerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Scheduler
        fields = '__all__'
