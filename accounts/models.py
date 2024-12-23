import uuid
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from phonenumber_field.modelfields import PhoneNumberField
from location.models import Location
from django.core.exceptions import ValidationError
from .managers import CustomUserManager
from mptt.models import MPTTModel, TreeForeignKey
# from officer.models import FieldOfficer

def name_validation(value):
    if not value or not value[0].isalpha():
        raise ValidationError("First name must start with an alphabet character.")


# class User(MPTTModel, AbstractBaseUser, PermissionsMixin): 
#     SUBSCRIPTION_STATUS_CHOICES = ( 
#         ('active', 'Active'),
#         ('inactive', 'Inactive'),
#     )      
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     first_name = models.CharField(max_length=50, validators=[name_validation])
#     last_name = models.CharField(max_length=50, validators=[name_validation])
#     email = models.EmailField(unique=True)
#     mobile = PhoneNumberField(unique=True)
#     photo = models.ImageField(blank=True, null=True, upload_to="users/photos/")
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superadmin = models.BooleanField(default=False)    
#     is_deleted = models.BooleanField(default=False) 
#     aadhar_number = models.CharField(max_length=16, blank=True)
#     ID_Proof = models.FileField(blank=True, null=True, upload_to="users/id_proofs/")    
#     location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
#     registration_datetime = models.DateTimeField(auto_now_add=True)  
#     subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='inactive')
#     parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
#     objects = CustomUserManager()
    
#     USERNAME_FIELD = "email"
#     EMAIL_FIELD = 'email'
#     REQUIRED_FIELDS = ["first_name", "last_name", "mobile"]

#     class Meta:
#         ordering = ['email']
#         verbose_name = ("User")
#         verbose_name_plural = ("Users")     

#     def get_full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def get_short_name(self):
#         return self.first_name

#     def __str__(self):
#         return self.email


class User(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = ( 
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )      
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100, validators=[name_validation])
    email = models.EmailField(unique=True)
    mobile = PhoneNumberField(unique=True)
    photo = models.ImageField(blank=True, null=True, upload_to="users/photos/")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)    
    is_deleted = models.BooleanField(default=False) 
    aadhar_number = models.CharField(max_length=16, blank=True)
    ID_Proof = models.FileField(blank=True, null=True, upload_to="users/id_proofs/")    
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    registration_datetime = models.DateTimeField(auto_now_add=True)  
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='inactive')