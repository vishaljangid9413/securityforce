from rest_framework import serializers
from .models import *
from business.models import Checkpoint, BusinessSite
from django.db import transaction
from master.serializers import UserMasterSerializer, BusinessMasterSerializer


class BusinessSiteCheckpointSerializer(serializers.ModelSerializer):
    business = BusinessMasterSerializer()

    class Meta:
        model = BusinessSite
        fields = ('name', 'business', 'is_active')


class ReportCheckpointSerializer(serializers.ModelSerializer):
    business_site = BusinessSiteCheckpointSerializer()
    
    class Meta:
        model = Checkpoint
        fields = ('name', 'floor', 'business_site', 'is_active')


class FeedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedImage
        fields = ('id', 'image', 'timestamp')


class FeedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedVideo
        fields = ('id', 'video', 'timestamp')


class FeedSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()
    checkpoint = ReportCheckpointSerializer()

    class Meta:
        model = Feed
        fields = ('id', 'user', 'checkpoint', 'message', 'voice_note', 'timestamp', 'viewed', 'images', 'videos')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        try:
            if instance.images.all():
                serializer = FeedImageSerializer(instance.images, many=True)
                representation["images"] = serializer.data
            if instance.videos.all():
                serializer = FeedVideoSerializer(instance.videos, many=True)
                representation["videos"] = serializer.data

        except Exception as e:
            print(str(e))

        return representation


class FeedPostSerializer(serializers.Serializer):
    # user_id = serializers.UUIDField()
    checkpoint_id = serializers.IntegerField()
    message = serializers.CharField(required=False)
    voice_note = serializers.FileField(required=False)
    images = serializers.ListField(
        child = serializers.ImageField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    videos = serializers.ListField(
        child = serializers.FileField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    def create(self, validated_data):
        # user_id = validated_data.get('user_id')
        user_id = self.context.get("user")
        checkpoint_id = validated_data.get('checkpoint_id')
        message = validated_data.get('message')
        voice_note = validated_data.get('voice_note')
        images = validated_data.get('images')
        videos = validated_data.get('videos')
        
        try:
            with transaction.atomic():
                try:
                    user = User.objects.get(id = user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('User not found')

                try:
                    checkpoint_obj = Checkpoint.objects.get(id = checkpoint_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('Checkpoint not found')

                feed_obj = Feed.objects.create(user = user, checkpoint = checkpoint_obj, message = message, voice_note = voice_note)
                
                if images:
                    feedImage_list = [FeedImage(image = image, feed=feed_obj) for image in images]
                    FeedImage.objects.bulk_create(feedImage_list)
                
                if videos:
                    feedVideo_list = [FeedVideo(video = video, feed=feed_obj) for video in videos]
                    FeedVideo.objects.bulk_create(feedVideo_list)

                return feed_obj
                
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)
        

class ComplaintImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintImage
        fields = ('id', 'image', 'timestamp')


class ComplaintVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintVideo
        fields = ('id', 'video', 'timestamp')


class ComplaintSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()
    checkpoint = ReportCheckpointSerializer()

    class Meta:
        model = Complaint
        fields = ('id', 'user', 'checkpoint', 'message', 'voice_note', 'timestamp', 'viewed', 'images', 'videos')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        try:
            if instance.images.all():
                serializer = ComplaintImageSerializer(instance.images, many=True)
                representation["images"] = serializer.data
            if instance.videos.all():
                serializer = ComplaintVideoSerializer(instance.videos, many=True)
                representation["videos"] = serializer.data

        except Exception as e:
            print(str(e))

        return representation


class ComplaintPostSerializer(serializers.Serializer):
    # user_id = serializers.UUIDField()
    checkpoint_id = serializers.IntegerField()
    message = serializers.CharField(required=False)
    voice_note = serializers.FileField(required=False)
    images = serializers.ListField(
        child = serializers.ImageField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    videos = serializers.ListField(
        child = serializers.FileField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    def create(self, validated_data):
        # user_id = validated_data.get('user_id')
        user_id = self.context.get("user")
        checkpoint_id = validated_data.get('checkpoint_id')
        message = validated_data.get('message')
        voice_note = validated_data.get('voice_note')
        images = validated_data.get('images')
        videos = validated_data.get('videos')

        try:
            with transaction.atomic():
                try:
                    user = User.objects.get(id = user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('User not found')

                try:
                    checkpoint_obj = Checkpoint.objects.get(id = checkpoint_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('Checkpoint not found')

                complaint_obj = Complaint.objects.create(user = user, checkpoint = checkpoint_obj, message = message, voice_note = voice_note)
                
                if images:
                    complaintImage_list = [ComplaintImage(image = image, complaint=complaint_obj) for image in images]
                    obj = ComplaintImage.objects.bulk_create(complaintImage_list)
                
                if videos:
                    complaintImage_list = [ComplaintVideo(video = video, complaint=complaint_obj) for video in videos]
                    obj = ComplaintVideo.objects.bulk_create(complaintImage_list)

                return complaint_obj
                
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)
        
        
class SOSImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSImage
        fields = ('id', 'image', 'timestamp')


class SOSVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSVideo
        fields = ('id', 'video', 'timestamp')


class SOSSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()
    images = SOSImageSerializer(many=True, read_only=True)
    videos = SOSVideoSerializer(many=True, read_only=True)
    checkpoint = ReportCheckpointSerializer()


    class Meta:
        model = SOS
        fields = ('id', 'user', 'checkpoint', 'message', 'voice_note', 'timestamp', 'viewed', 'images', 'videos')

        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        try:
            if instance.images.all():
                serializer = SOSImageSerializer(instance.images, many=True)
                representation["images"] = serializer.data
            if instance.videos.all():
                serializer = SOSVideoSerializer(instance.videos, many=True)
                representation["videos"] = serializer.data

        except Exception as e:
            print(str(e))

        return representation


class SOSPostSerializer(serializers.Serializer):
    # user_id = serializers.UUIDField()    
    checkpoint_id = serializers.IntegerField()
    message = serializers.CharField(required=False)
    voice_note = serializers.FileField(required=False)
    images = serializers.ListField(
        child = serializers.ImageField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    videos = serializers.ListField(
        child = serializers.FileField(max_length=10000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    def create(self, validated_data):
        # user_id = validated_data.get('user_id')
        user_id = self.context.get("user")
        checkpoint_id = validated_data.get('checkpoint_id')
        message = validated_data.get('message')
        voice_note = validated_data.get('voice_note')
        images = validated_data.get('images')
        videos = validated_data.get('videos')

        try:
            with transaction.atomic():
                try:
                    user = User.objects.get(id = user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('User not found')

                try:
                    checkpoint_obj = Checkpoint.objects.get(id = checkpoint_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError('Checkpoint not found')

                sos_obj = SOS.objects.create(user = user, checkpoint = checkpoint_obj, message = message, voice_note = voice_note)
                
                if images:
                    sosImage_list = [SOSImage(image = image, sos=sos_obj) for image in images]
                    obj = SOSImage.objects.bulk_create(sosImage_list)
                
                if videos:
                    sosImage_list = [SOSVideo(video = video, sos=sos_obj) for video in videos]
                    obj = SOSVideo.objects.bulk_create(sosImage_list)

                return sos_obj
                
        except Exception as e:
            transaction.rollback()
            raise serializers.ValidationError(e)
        