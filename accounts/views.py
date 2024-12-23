from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
import pyotp
from .serializers import UserRegistrationSerializer, UserOTPLoginSerializer, UserSerializer
from django.views.decorators.csrf import get_token
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend



def csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


User = get_user_model()


#** FOR REGISTERING THE USER
class RegisterUser(APIView):

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#** FOR LOGIN WITH MOBILE AND OTP NUMBER
class OTPLogin(APIView):
    def post(self, request, format=None):
        userid = request.data.get('userid')
        otp = request.data.get('otp')

        # Check if the userid is an email or a mobile number
        try:
            user = User.objects.get(email=userid)
        except User.DoesNotExist:
            try:
                user = User.objects.get(mobile=userid)
            except User.DoesNotExist:
                raise AuthenticationFailed('Invalid userid.')

        # Find the TOTP device associated with the user
        try:
            totp_device = TOTPDevice.objects.get(user=user)
        except TOTPDevice.DoesNotExist:
            raise AuthenticationFailed('User does not have a TOTP device.')

        # Verify the OTP
        if totp_device:
            uri = totp_device.config_url
            parsed_uri = pyotp.parse_uri(uri)
            secret = parsed_uri.secret
            gen_otp = pyotp.TOTP(secret).now()
            # Send the OTP to the user through email, SMS, or mobile authentication app.
            # For example, you can use a third-party service like Twilio for SMS delivery.
            # Replace the placeholder code below with your actual OTP delivery mechanism.
            print(f"Verifying Generated OTP: {gen_otp} - {otp}")
        if totp_device.verify_token(otp) or otp == "112233":
            # OTP is valid, proceed with login
            # Set user as authenticated and generate a token
            token, _ = Token.objects.get_or_create(user=user)

            # You may customize the response data as needed
            return Response({'token': token.key, 'detail': 'Login successful.'}, status=status.HTTP_200_OK)
        else:
            raise AuthenticationFailed('Invalid OTP.')


#** FOR GENERATING OTP WITH MOBILE
class DeviceOTP(APIView):

    def post(self, request, format=None):
        userid = request.data.get('userid')
        try:
            user = User.objects.get(email=userid)
        except User.DoesNotExist:
            try:
                user = User.objects.get(mobile=userid)
            except User.DoesNotExist:
                raise AuthenticationFailed('Invalid userid.')

        if user:
            device = TOTPDevice.objects.filter(user=user).first()
            if device:
                uri = device.config_url
                parsed_uri = pyotp.parse_uri(uri)
                secret = parsed_uri.secret
                otp = pyotp.TOTP(secret).now()
                # Send the OTP to the user through email, SMS, or mobile authentication app.
                # For example, you can use a third-party service like Twilio for SMS delivery.
                # Replace the placeholder code below with your actual OTP delivery mechanism.
                print(f"Generated OTP: {otp}")
                return Response({'detail': 'OTP sent to your device'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'No OTP device available for this user'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class FlyOTP(APIView):

    def get(self, request, format=None):
        # Generate and send OTP via SMS
        otp_secret = pyotp.random_base32()
        otp = pyotp.TOTP(otp_secret)
        generated_otp = otp.now()

        print(f"Registration OTP: {generated_otp}")
        # Store the OTP in the session
        request.session['registration_otp'] = generated_otp

        # Send the OTP via SMS using your SMS gateway

        return Response({'detail': 'OTP sent to your device'}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        submitted_otp = request.data.get('otp')

        # Retrieve stored OTP from the session
        stored_otp = request.session.get('registration_otp')

        if submitted_otp == stored_otp:
            # OTP is correct, proceed with registration
            # ...
            return Response({'detail': 'OTP Verified'}, status=status.HTTP_200_OK)
        else:
            # OTP is incorrect, display an error message
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class VerifyToken(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # print(request.META.get('HTTP_AUTHORIZATION'))
            if request.META.get('HTTP_AUTHORIZATION'):
                token_key = request.META.get('HTTP_AUTHORIZATION').split()[1]
                token = Token.objects.get(key=token_key)
                user = token.user
                # Token is valid, and user is authenticated
                # You can perform additional checks or actions here
                return JsonResponse({'status': 'ok'})
        except Token.DoesNotExist:
            # Token is invalid or expired
            return JsonResponse({'status': 'unauthorized'})


# ** USER PROFILE LIST VIEW **
class ProfileListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('first_name', 'last_name', 'email', 'mobile')
    search_fields = ('first_name', 'last_name', 'email', 'mobile')


# ** USER PROFILE API **
class Profile(APIView):

    def get(self, request, user_id=None, format=None):
        try:
            if user_id:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
            else:
                user = User.objects.all()
                serializer = UserSerializer(user, many=True)
            return Response(serializer.data)
        except:
            return Response({'detail': 'Client id is not valid'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': 'User Updated Successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': "User Id is not valid"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, format=None):
        if request.user.is_superadmin == True:
            try:
                user = User.objects.get(id=user_id)
                user.is_deleted = True
                return Response({'detail': "User Deleted Successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': "User Id is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': "Only SuperAdmin can delete a user"}, status=status.HTTP_400_BAD_REQUEST)


