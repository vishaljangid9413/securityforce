from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Business, BusinessSite, Checkpoint, Route, Client, UserInBusiness, SiteInRoute
from officer.models import FieldOfficer, Shift, FieldOfficerRoute
from officer.serializers import FieldOfficerSerializer, ShiftSerializer, FORoutesSerializer, BasicInfoFieldOfficerSerializer
from officer.models import SiteVisitData, CheckpointVisitData, FieldOfficer
from django.db.models import Q
from location.serializers import LocationSerializer
from master.serializers import UserMasterSerializer, BusinessMasterSerializer,ShiftMasterSerializer
from django.db import transaction
from datetime import date
from datetime import datetime, timedelta
from calendar import monthrange

User = get_user_model()

class BaseBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ('name', 'logo',)
        
class BusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = '__all__'


class BaseBusinessSiteSerializer(serializers.ModelSerializer):
    # business = BaseBusinessSerializer()
    location = LocationSerializer()

    class Meta:
        model = BusinessSite
        fields = ('id', 'name', 'business', 'address', 'location',)

class BusinessSiteSerializer(serializers.ModelSerializer):
    # business = BusinessMasterSerializer()
    location = LocationSerializer()
    shift = ShiftSerializer()
    # Serializer for PointField
    geo_code = serializers.SerializerMethodField()
    # Serializer for PolygonField
    area = serializers.SerializerMethodField()
    # Serializer for completed Rounds
    rounds_completed = serializers.SerializerMethodField()

    class Meta:
        model = BusinessSite
        fields = ('id', 'name', 'business', 'geo_code', 'area', 'address',
                  'location', 'is_active', 'rounds', 'rounds_completed', 'schedule','shift', 'floors')

    def get_rounds_completed(self, obj):
        try:

            if obj.schedule == "daily":
                rounds = SiteVisitData.objects.filter(site=obj, date=date.today())
                return BaseSiteVisitDataSerializer(rounds, many=True).data

            if obj.schedule == "weekly":
                # Get the start and end date for the week
                start_date = datetime.today() - timedelta(days=datetime.today().weekday())
                end_date = start_date + timedelta(days=6)
                # Filter data for the week
                rounds = SiteVisitData.objects.filter(site=obj, date__range=[start_date, end_date])
                return BaseSiteVisitDataSerializer(rounds, many=True).data

            if obj.schedule == "monthly":
                # Get the start and end date for the month
                today = datetime.today()
                start_date = today.replace(day=1)  # First day of the month
                end_date = today.replace(day=monthrange(today.year, today.month)[1])  # Last day of the month
                # Filter data for the month
                rounds = SiteVisitData.objects.filter(site=obj, date__range=[start_date, end_date])
                return BaseSiteVisitDataSerializer(rounds, many=True).data

        except Exception as e:
            print(str(e))

        return None
    
    def get_geo_code(self, obj):
        # Serialize PointField as a set
        if obj.geo_code:
            try:
                return {'latitude': obj.geo_code.y, 'longitude': obj.geo_code.x}
            except:
                return {'latitude': 0, 'longitude': 0}
        else:
            return None

    def get_area(self, obj):
        # Serialize PolygonField as an array of coordinate sets
        if obj.area:
            try:
                arr = [{'latitude':item[1], 'longitude':item[0]} for item in obj.area.coords[0]]                
                return arr  # Assuming that the first list of coordinates is the exterior ring
            except:
                return []
        else:
            return None


class BusinessSitePostSerializer(serializers.ModelSerializer):    
    # area = serializers.SerializerMethodField()

    class Meta:
        model = BusinessSite
        fields = '__all__'

    # def get_area(self, obj):
    #     # Serialize PolygonField as an array of coordinate sets
    #     if obj.area:
    #         try:
    #             arr = [{'latitude':item[1], 'longitude':item[0]} for item in obj.area.coords[0]]                
    #             return arr  # Assuming that the first list of coordinates is the exterior ring
    #         except:
    #             return []
    #     else:
    #         return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['zipcode'] = instance.location.zipcode   
            logs = instance.logs.filter(date=date.today())
            logsSerializer = SiteVisitDataPostSerializer(logs, many=True)
            # logsSerializer.data['status'] = "COMPLETED" if logsSerializer.data.end_time else "IN PROGRESS"
            representation['report'] = logsSerializer.data
            representation['latitude'] = instance.geo_code.x if instance.geo_code else 0
            representation['longitude'] = instance.geo_code.y if instance.geo_code else 0            
        except Exception as e:
            print(e)
        return representation


class CheckpointPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Checkpoint
        fields = '__all__'


class CheckpointSerializer(serializers.ModelSerializer):
    # business_site = BusinessSiteSerializer()    

    class Meta:
        model = Checkpoint
        fields = ('id', 'name', 'floor', 'business_site', 'geo_code', 'is_active')          
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        site = instance.business_site        
        representation['schedule'] = site.schedule
        representation['rounds'] = site.rounds        
        is_completed = False
        rounds = 0
        print(instance.logs.filter(date=date.today()).count() == (site.logs.filter(date=date.today())).count())
        # print(instance.logs.filter(checkpoint=obj, date=date.today()).count())
        try:
            if site.schedule == "daily":
                rounds = instance.logs.filter(date=date.today()).count()
                site_rounds = (site.logs.filter(date=date.today())).count()        
                is_completed = (rounds == site_rounds) if site_rounds!=0 else False

            if site.schedule == "weekly":
                # Get the start and end date for the week
                start_date = datetime.today() - timedelta(days=datetime.today().weekday())
                end_date = start_date + timedelta(days=6)
                # Filter data for the week
                rounds = instance.logs.filter(date__range=[start_date, end_date]).count()
                site_rounds = (site.logs.filter(date__range=[start_date, end_date])).count()
                is_completed = (rounds == site_rounds)  if site_rounds!=0 else False

            if site.schedule == "monthly":
                # Get the start and end date for the month
                today = datetime.today()
                start_date = today.replace(day=1)  # First day of the month
                end_date = today.replace(day=monthrange(today.year, today.month)[1])  # Last day of the month
                # Filter data for the month
                rounds = instance.logs.filter(date__range=[start_date, end_date]).count()
                site_rounds = (site.logs.filter(date__range=[start_date, end_date])).count()
                is_completed = (rounds == site_rounds) if site_rounds!=0 else False

        except Exception as e:
            print(str(e))

        representation['is_completed'] = is_completed
        representation['completed_rounds'] = rounds
        return representation


class CheckpointSerializerV2(serializers.ModelSerializer):    
    geo_code = serializers.SerializerMethodField()
    class Meta:
        model = Checkpoint
        fields = ('id', 'name', 'floor', 'geo_code', 'is_active')

    def get_geo_code(self, obj):
        # Serialize PointField as a set
        if obj.geo_code:
            return {'latitude': obj.geo_code.y, 'longitude': obj.geo_code.x}
        else:
            return None

class SitesInRouteSerializerV2(serializers.ModelSerializer):
    site = BaseBusinessSiteSerializer(many=False, read_only=True)
    class Meta:
        model = SiteInRoute
        fields = ('site', ) 


class OfficerInRouteSerializerV2(serializers.ModelSerializer):
    fieldofficer = BasicInfoFieldOfficerSerializer(many=False, read_only=True)
    class Meta:
        model = FieldOfficerRoute
        fields = ('fieldofficer',)  

class RouteWithSiteSerializer(serializers.ModelSerializer):
    # sites = SitesInRouteSerializerV2(many=True, read_only=True)
    # officers = OfficerInRouteSerializerV2(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ('id', 'name', 'is_active')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        sites = instance.sites        
        # temps = [item['site'] for item in SitesInRouteSerializerV2(sites, many=True).data]
        # representation['sites'] = [item['site'] for item in SitesInRouteSerializerV2(sites, many=True).data]
        representation['sites'] = [{
                "id": item["site"]["id"],
                "name": item["site"]["name"],
                "address": item["site"]["address"],
                "business": item["site"]["business"] if item["site"]["business"] else None,
                # "logo": item["site"]["business"] if item["site"]["business"] else None,
                "zipcode": item["site"]["location"]["zipcode"] if item["site"]["location"] else None,
            } for item in SitesInRouteSerializerV2(sites, many=True).data]
        
        print([item["site"]["name"] for item in SitesInRouteSerializerV2(sites, many=True).data])
        fieldofficers = instance.officers        
        representation['officers'] = [item['fieldofficer'] for item in OfficerInRouteSerializerV2(fieldofficers, many=True).data]
        return representation


class RouteSerializer(serializers.ModelSerializer):
    business = BusinessMasterSerializer()

    class Meta:
        model = Route
        fields = ('id', 'name', 'business')
  

class RoutePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ('id', 'name', 'business', 'is_active')


class BusinessSiteClientSerializer(serializers.ModelSerializer):
    # Serializer for PolygonField
    area = serializers.SerializerMethodField()

    class Meta:
        model = BusinessSite
        fields = ('id', 'name', 'business', 'area', 'address',
                  'location', 'is_active', 'shift', 'rounds', 'schedule', 'floors')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        checkpoints = instance.checkpoints        
        representation['checkpoints'] = CheckpointSerializerV2(checkpoints, many=True).data
        representation['latitude']= instance.geo_code.y if instance.geo_code else 0
        representation['longitude']= instance.geo_code.x if instance.geo_code else 0
        # representation['shift'] = ShiftMasterSerializer(instance.shift, many=False).data
        return representation    

    def get_area(self, obj):
        # Serialize PolygonField as an array of coordinate sets
        if obj.area:
            try:
                arr = [{'latitude':item[1], 'longitude':item[0]} for item in obj.area.coords[0]]                
                return arr  # Assuming that the first list of coordinates is the exterior ring
            except:
                return []
        else:
            return None


class ClientSerializer(serializers.ModelSerializer):
    # agency = BusinessSerializer()
    client = BusinessMasterSerializer()

    class Meta:
        model = Client
        fields = ('id', 'client', 'started_date', 'end_date', 'is_active',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        sites = instance.client.business_sites        
        representation['sites'] = BusinessSiteClientSerializer(sites, many=True).data        
        return representation


class ClientPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('agency', 'client', 'started_date', 'end_date', 'is_active',)


class UserInBusinessBaseSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()
    business = BusinessSerializer(id)
    class Meta:
        model = UserInBusiness
        fields = ('id', 'user', 'business', 'role', 'is_active')
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user = instance.user
            representation['officer'] = "null"
            representation['manager'] =  "null"
            if not instance.role == "admin":
                representation['officer'] = user.field_officer.id
                representation['manager'] =  user.field_officer.manager.id
                    
        except Exception as e:
            print(e)
        return representation


class UserInBusinessSerializer(serializers.ModelSerializer):
    user = UserMasterSerializer()

    class Meta:
        model = UserInBusiness
        fields = ('user', 'business', 'role', 'is_active')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            fo = instance.user.field_officer
            representation['id'] = fo.id
            representation['manager'] = UserMasterSerializer(fo.manager).data
            representation['shift'] = ShiftSerializer(fo.shift).data
            representation['routes'] = FORoutesSerializer(fo.routes, many=True).data
        except Exception as e:
            print(e)
        return representation


class UserInBusinessSerializerBase(serializers.ModelSerializer):

    class Meta:
        model = UserInBusiness
        fields = ('user', 'business', 'role', 'is_active')

    def to_representation(self, instance):        
        representation = super().to_representation(instance)
        try:
            representation["name"] = instance.business.name
            representation["address"] = instance.business.address            
        except Exception as e:
            print("Unable to set business info - ",str(e))
        return representation


class UserInBusinessPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInBusiness
        fields = '__all__'
        
    def handle_manager(self, request, instance ,data):
        if data.get("role", None):
            if data['role'] == 'field_officer' and instance.role == 'manager':
                for officers in instance.user.field_officers_manager.all():
                    officers.manager = request.user
                    officers.save()
                    
        instance.role = data['role']   
        instance.save() 
        return "true"


class FieldOfficerPostSerializer(serializers.Serializer):
    user = serializers.CharField(required=False)
    manager = serializers.UUIDField(required=False)
    shift = serializers.IntegerField(required=False)
    officer = serializers.UUIDField(required=False)
    username = serializers.CharField(required=False)
    email = serializers.EmailField()
    mobile = serializers.CharField()
    password = serializers.CharField()
    aadhar_number = serializers.CharField(max_length=20, required=False)
    photo = serializers.FileField(required=False)
    ID_Proof = serializers.FileField(required=False)
    role = serializers.ChoiceField(choices=UserInBusiness.ROLE_CHOICES, required=False) 

    def create(self, validated_data):
        user_id = validated_data.get('user')
        manager_id = validated_data.get('manager')
        shift_id = validated_data.get('shift')
        username = validated_data.get('username')
        email = validated_data.get('email')
        aadhar_number = validated_data.get('aadhar_number')
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')
        aadhar_number = validated_data.get('aadhar_number')
        photo = validated_data.get('photo')
        ID_Proof = validated_data.get('ID_Proof')
        role = validated_data.get('role')
        print("shift_id: ",validated_data)
        try:
            with transaction.atomic():
                # If user_id is provided, try to get the user
                if user_id:
                    try:
                        user = User.objects.get(Q(mobile=user_id) | Q(email=user_id))
                    except User.DoesNotExist:
                        raise serializers.ValidationError('User not found')
                else:
                    username_split = username.split(' ')
                    first_name = username_split[0]
                    last_name = ' '.join(username_split[1:])

                    # Create a new user
                    try:
                        user = User.objects.create_user(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            mobile=mobile,
                            # Set the password later or generate a random one
                            password=password,
                            aadhar_number=aadhar_number,
                            photo=photo,
                            ID_Proof=ID_Proof,
                        )
                    except Exception as e:
                        raise Exception(f"User creation failed: {str(e)}")

                # Create a new field officer
                UserInBusiness.objects.create(
                    user=user,
                    business=self.context['business'].business,
                    role=role,
                    is_active=True
                )

                try:
                    shift = Shift.objects.get(id=shift_id)
                except:
                    raise Exception({'detail':'Enter a valid Shift Id'})

                if manager_id:
                    try:
                        manager = User.objects.get(id=manager_id)
                    except:
                        raise Exception({'detail':'Enter a valid Manager Id'})
                else:
                    manager = self.context['user']

                officer = FieldOfficer.objects.create(user=user, manager=manager, shift=shift)
                
                data ={
                    "officer_id": officer.id,
                    "username":username,
                    "email": email,
                    "mobile":mobile,
                    "aadhar_number":aadhar_number,
                    "password":"Hidden"
                }
                return data
        except Exception as e:
            transaction.rollback()  
            raise serializers.ValidationError(e)


class SiteInRouteSerializer(serializers.ModelSerializer):
    # route = RouteSerializer()
    site= BusinessSiteSerializer()
    
    class Meta:
        model = SiteInRoute
        fields = ('id', 'route', 'site')


class SiteInRoutePostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SiteInRoute
        fields = '__all__'


class RouteAssignmentSerializer(serializers.Serializer):
    route_id = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())


class ManagerFieldOfficerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInBusiness
        fields = ('user',)

        
class SiteVisitDataPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= SiteVisitData
        fields = '__all__'

        
class BaseSiteVisitDataSerializer(serializers.ModelSerializer):    
    class Meta:
        model= SiteVisitData
        fields = ('id', 'user', 'date', 'start_time', 'end_time')

class SiteVisitDataSerializer(serializers.ModelSerializer):
    # user = UserMasterSerializer()
    site = BaseBusinessSiteSerializer()  
    class Meta:
        model= SiteVisitData
        fields = ('id', 'site', 'user', 'date', 'start_time', 'end_time')


class CheckpointVisitDataPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CheckpointVisitData
        fields = '__all__'


class CheckpointVisitDataSerializer(serializers.ModelSerializer):    
    # checkpoint = CheckpointSerializer()
    
    class Meta:
        model = CheckpointVisitData
        fields = ('user', 'checkpoint', 'time')
