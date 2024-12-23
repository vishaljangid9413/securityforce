from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from master.models import Shift
from business.models import Route, BusinessSite, Checkpoint


User = get_user_model()


class FieldOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name= "field_officer")
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="field_officers_manager")
    shift = models.ForeignKey(Shift, null=True, on_delete=models.SET_NULL, related_name="field_officer")

    def hasSites(self):
        return 
    
    def hasRoutes(self):
        return 

    def __str__(self):
        return f"{self.user.email}"


class FieldOfficerRoute(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True, blank=True , related_name="officers")
    fieldofficer = models.ForeignKey(FieldOfficer, null=True, on_delete=models.CASCADE, related_name="routes")

    class Meta:
        unique_together = ('route', 'fieldofficer')
    
    def __str__(self):
        return f"{self.route.name} assigned to {self.fieldofficer}"


class FieldOfficerSite(models.Model):
    site = models.ForeignKey(BusinessSite, on_delete=models.CASCADE, null=True, blank=True , related_name="officers")
    fieldofficer = models.ForeignKey(FieldOfficer, null=True, on_delete=models.CASCADE, related_name="sites")

    class Meta:
        unique_together = ('site', 'fieldofficer')
        
    def __str__(self):
        return f"{self.site.name} assigned to {self.fieldofficer}"


class SiteVisitData(models.Model):
    site = models.ForeignKey(BusinessSite, on_delete=models.CASCADE, related_name="logs")    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="siteLogs")
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    start_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.site.name)


class CheckpointVisitData(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="checkpointLogs")
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, null=True, blank=True, related_name="logs")
    start_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return str(self.checkpoint)


class RouteLog(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'NOT STARTED'),        
        ('in_progress', 'IN PROGRESS'),        
        ('incomplete', 'INCOMPLETE'),
        ('completed', 'COMPLETED'),
        ('sos', 'SOS')
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="routeLogs")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True, blank=True , related_name="logs")
    start_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    start_point = models.PointField(blank=True, null=True)
    end_point = models.PointField(blank=True, null=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    kilometers = models.FloatField(default=0.0, null=True, blank=True)
    status = models.CharField(default="not_started", choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('user', 'route', 'date')

class DutyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='dutyLogs')
    date = models.DateField(auto_now_add=True)
    start_time = models.TimeField(auto_now_add=True)
    end_time = models.TimeField(blank=True, null=True)
    start_point = models.PointField(blank=True, null=True)
    end_point = models.PointField(blank=True, null=True)
    selfie_start = models.ImageField(upload_to='users/duty/selfies/start', null=True, blank=True)
    selfie_end = models.ImageField(upload_to='users/duty/selfies/end', null=True, blank=True)
    kilometers = models.IntegerField(default= 0, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user} travelled {self.kilometers} Kilometers"

