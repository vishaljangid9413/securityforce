from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Shift, FieldOfficer, DutyLog, RouteLog, FieldOfficerRoute, FieldOfficerSite, SiteVisitData, CheckpointVisitData
from business.models import Route, UserInBusiness
from master.serializers import UserMasterSerializer
from datetime import date

User = get_user_model()


class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = '__all__'


class FieldOfficerBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldOfficer
        fields = '__all__'


class FieldOfficerSerializer(serializers.ModelSerializer):
    # user = UserMasterSerializer()
    # manager = UserMasterSerializer()

    class Meta:
        model = FieldOfficer
        fields = ('user', 'manager', 'shift')


class AssignManagerFieldOfficerSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()

    class Meta:
        model = UserInBusiness
        fields = ('user', 'business', 'role', 'is_active')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            fo = instance.user.field_officer
            officersUnderManager = FieldOfficer.objects.filter(manager = instance.user)
            # data = []
            # for officer in officersUnderManager:
            #     data.append(UserMasterSerializer(officer.user).data)
            representation['id'] = fo.id
            # representation['officer'] = data
            representation['manager'] = UserMasterSerializer(fo.manager).data
            representation['shift'] = ShiftSerializer(fo.shift).data
            representation['routes'] = FORoutesSerializer(fo.routes, many=True).data
        except Exception as e:  
            print(e)
        return representation


class BasicInfoFieldOfficerSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()

    class Meta:
        model = FieldOfficer
        fields = ('id','user',)


class RoutesForOfficerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = '__all__'


class FORoutesSerializer(serializers.ModelSerializer):
    route = RoutesForOfficerSerializer()

    class Meta:
        model = FieldOfficerRoute
        fields = ('route', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            sites = instance.route.sites.all()
            representation['sites'] = [site.site.id for site in sites]
            route_log = None
            try:
                route_log = RouteLog.objects.get(user=instance.fieldofficer.user, route=instance.route, date=date.today())
            except RouteLog.DoesNotExist as e:
                print(str(e))
            
            representation['status'] = route_log.status if route_log else "NOT STARTED"
            representation['kilometers'] = route_log.kilometers  if route_log else 0
            representation['start_time'] = route_log.start_time if route_log else "00:00:00"
            representation['end_time'] = route_log.end_time if route_log else "00:00:00"
        except Exception as e:
            print(e)
        return representation

    

class RouteLogSerializer(serializers.ModelSerializer):
    route = RoutesForOfficerSerializer()
    class Meta:
        model = RouteLog
        fields = ('id', 'user', 'route', 'status', 'start_time', 'end_time', 'kilometers', 'date')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            sites = instance.route.sites.all()            
            representation['sites'] = [site.site.id for site in sites]            
        except Exception as e:
            print(e)
        return representation

class DutyLogBaseSerializer(serializers.ModelSerializer):
    start_point = serializers.SerializerMethodField()
    end_point = serializers.SerializerMethodField()


    class Meta:
        model = DutyLog
        fields = ('id', 'user', 'date', 'start_time', 'end_time', 'start_point', 'end_point',
                  'selfie_start', 'selfie_end', 'kilometers')

    def get_start_point(self, instance):
       return {'latitude': instance.start_point.y, 'longitude': instance.start_point.x} if instance.start_point else None
    
    def get_end_point(self, instance):
        return {'latitude': instance.end_point.y, 'longitude': instance.end_point.x} if instance.end_point else None

class DutyLogSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()
    start_point = serializers.SerializerMethodField()
    end_point = serializers.SerializerMethodField()


    class Meta:
        model = DutyLog
        fields = ('id', 'user', 'date', 'start_time', 'end_time', 'start_point', 'end_point',
                  'selfie_start', 'selfie_end', 'kilometers')

    def get_start_point(self, instance):
       return {'latitude': instance.start_point.y, 'longitude': instance.start_point.x} if instance.start_point else None
    
    def get_end_point(self, instance):
        return {'latitude': instance.end_point.y, 'longitude': instance.end_point.x} if instance.end_point else None


class DutyLogPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = DutyLog
        fields = ('id', 'user', 'date', 'start_time', 'end_time', 'start_point', 'end_point',
                  'selfie_start', 'selfie_end', 'kilometers')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:            
            representation['spoint'] = {'latitude': instance.start_point.y, 'longitude': instance.start_point.x} if instance.start_point else None
            representation['epoint'] = {'latitude': instance.end_point.y, 'longitude': instance.end_point.x} if instance.end_point else None
        except Exception as e:
            print(e)
        return representation
    
    


class RouteAssignSerializer(serializers.ModelSerializer):
    fieldofficer = UserMasterSerializer()

    class Meta:
        model = FieldOfficerRoute
        fields = ('id', 'fieldofficer')
        

class RouteAssignPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldOfficerRoute
        fields = ('id', 'route', 'fieldofficer')


class SiteAssignSerializer(serializers.ModelSerializer):
    fieldofficer = UserMasterSerializer()

    class Meta:
        model = FieldOfficerSite
        fields = ('id', 'site', 'fieldofficer')


class SiteAssignPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldOfficerSite
        fields = ('id',  'site', 'fieldofficer')
