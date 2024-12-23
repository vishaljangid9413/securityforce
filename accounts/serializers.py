from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice
from location.serializers import LocationSerializer
from master.serializers import ShiftMasterSerializer
from officer.serializers import DutyLogBaseSerializer
from business.serializers import UserInBusinessSerializer, UserInBusinessSerializerBase
from datetime import date
User = get_user_model()

# FOR LOGIN USER


class UserSerializer(serializers.ModelSerializer):
    location = LocationSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile', 'photo', 'is_active', 'is_superadmin', 'is_superuser', 'is_staff', 'last_login', 'aadhar_number', 'ID_Proof', 'registration_datetime', 'location', 'subscription_status')

    def to_representation(self, instance):        
        representation = super().to_representation(instance)
        try:
            representation["role"] = "Individual"
            representation['is_BusinessUser'] = False
            if hasattr(instance, 'business') and instance.business:
                representation["role"] = instance.business.role
                if instance.business.role=="admin":
                    business = instance.business.business
                    representation['is_BusinessUser'] = True
                    representation['business_type'] = "agency" if business.is_agency else "client" if business.clients else "business"
                serializer = UserInBusinessSerializerBase(instance.business)
                representation["business"] = serializer.data 
            if hasattr(instance, 'field_officer') and instance.field_officer:
                representation["shift"] = ShiftMasterSerializer(instance.field_officer.shift, many=False).data
                duty = instance.dutyLogs.all().filter(date=date.today())
                representation["dutylog"] = DutyLogBaseSerializer(duty, many=True).data
                print(DutyLogBaseSerializer(duty, many=True).data)

        except Exception as e:
            print(str(e))
            representation['is_BusinessUser'] = False

        return representation


# FOR VALIDATING AND CREATING A USER
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'email', 'mobile', 'password')

    def create(self, validated_data):
        # request = self.context.get('request')
        # if request:
        #     print(f"CREATE USER SERIALIZER: {request.session['registration_otp']}")
        # else:
        #     print("NO REQUEST FOUND")
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email'),
            mobile=validated_data.get('mobile'),
            password=validated_data['password']
        )

        # You can provide a name for the device
        device = TOTPDevice(user=user, name='default')
        device.save()
        # device.token_set(otp)  # Set the OTP manually for the device
        return user


class UserOTPLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        otp = data.get('otp')

        if username and otp:
            user = User.objects.filter(username=username).first()

            if user:
                if user.is_active:
                    device = TOTPDevice.objects.filter(user=user).first()

                    if device and device.verify_token(otp):
                        data['user'] = user
                    else:
                        raise serializers.ValidationError('Invalid OTP.')
                else:
                    raise serializers.ValidationError('User is inactive.')
            else:
                raise serializers.ValidationError('User does not exist.')
        else:
            raise serializers.ValidationError(
                'Must include "username" and "otp".')

        return data
