from django.contrib.gis.db import models
from location.models import Location
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from master.models import Shift 
import re
User = get_user_model()


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9]*$', value):
        raise ValidationError('Field must only contain alphanumeric characters.')


class Business(models.Model):    
    name = models.CharField(max_length=100, unique=True)
    registration_number = models.CharField(max_length=100, unique=True, validators=[validate_alphanumeric])
    registration_certificate = models.FileField(upload_to='documents/business/registration/', null=True, blank=True)
    address = models.CharField(max_length=100)
    geo_code = models.PointField(null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    is_agency = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='images/business/logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    phone = PhoneNumberField(blank=True)
    email = models.EmailField(blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class BusinessSite(models.Model):  
    SCHEDULE_CHOICES = ( 
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    )
    name = models.CharField(max_length=100)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_sites', null=True, blank=True)
    geo_code = models.PointField(blank=True, null=True)  # Represents the geographical location
    area = models.PolygonField(blank=True, null=True)    # Represents the geographical boundary of the site
    address = models.CharField(max_length=100)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    rounds = models.IntegerField(default=1)
    schedule  = models.CharField(max_length=100, choices=SCHEDULE_CHOICES, default='daily') #(Daily, Weekly, bi-Weekly, Monthly)"
    floors = models.IntegerField(default=1)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, related_name='business_sites', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.geo_code and self.area:
            if not self.area.contains(self.geo_code):
                raise ValidationError("The geo_code is not within the site's area.")
        super().save(*args, **kwargs)


class Checkpoint(models.Model):
    name  = models.CharField(max_length=100)
    floor = models.IntegerField(default=1)
    business_site = models.ForeignKey(BusinessSite, related_name='checkpoints', on_delete=models.CASCADE)
    geo_code = models.PointField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.business_site and self.geo_code:
            if not self.business_site.area.contains(self.geo_code):
                raise ValueError("Checkpoint is outside the site's area")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    business = models.ForeignKey(Business, null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class SiteInRoute(models.Model):
    route = models.ForeignKey(Route, related_name='sites', on_delete=models.CASCADE, null=True, blank=True)
    site = models.OneToOneField(BusinessSite, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('route', 'site')
    def __str__(self):
        return f"{self.site.name} in {self.route.name}"


class Client(models.Model):
    agency = models.ForeignKey(Business, related_name='agencies', on_delete=models.CASCADE)
    client = models.ForeignKey(Business, related_name='clients', on_delete=models.CASCADE)
    started_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('agency', 'client')

    def __str__(self):
        return f"{self.agency.name} ({self.client.name})" 


class UserInBusiness(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('field_officer', 'Field Officer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default="admin")
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.user} works with {self.business} as a {self.role}"
        