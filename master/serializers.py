from rest_framework import serializers
from .models import HelpCategory, Shift
from accounts.models import User
from business.models import Business

class ShiftMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shift
        fields = ('id', 'title', 'start_time', 'end_time', 'duration')


# ** ITS A MASTER USER SERIALIZER, it provides a limited detail of a user **
class UserMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile', 'photo', 'ID_Proof', 'is_active')

        
# ** ITS A MASTER BUSINESS SERIALIZER, it provides a limited detail of a business **
class BusinessMasterSerializer(serializers.ModelSerializer):
    # Serializer for PointField   

    class Meta:
        model = Business
        fields = ('id', 'name', 'email', 'phone', 'registration_number', 'address', 'is_agency', 'website', 'is_deleted')    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['latitude'] = instance.geo_code.y if instance.geo_code else None
        representation['longitude'] = instance.geo_code.x if instance.geo_code else None
        return representation


class HelpCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HelpCategory
        fields = ('name',)