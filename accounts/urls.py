from django.urls import path
from .views import RegisterUser, OTPLogin, DeviceOTP, FlyOTP, VerifyToken, csrf_token_view, Profile, ProfileListView

urlpatterns = [
    path('api/register/', RegisterUser.as_view(), name='user-register'),
    path('api/login/', OTPLogin.as_view(), name='user-login'),
    path('api/login_otp/', DeviceOTP.as_view(), name='device-otp'),
    path('api/otp/', FlyOTP.as_view(), name='otp'),
    path('rest-auth/login/', OTPLogin.as_view(), name='rest_login'),
    path('verifyToken/', VerifyToken.as_view(), name='verify-token'),
    path('csrftoken/', csrf_token_view, name='user-register'),


    path('api/profileList/', ProfileListView.as_view(), name='user-profile-list'),
    path('api/profile/', Profile.as_view(), name='user-profile'),
    path('api/profile/<str:user_id>/', Profile.as_view(), name='user-profile'),
    # path('api/profile/<str:pk>/', ProfileWithAttr.as_view(),
    #      name='user-profile-with-attr'),
]
