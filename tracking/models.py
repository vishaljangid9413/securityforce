from django.contrib.gis.db import models
from django.shortcuts import render
from django.contrib.auth import get_user_model
User = get_user_model()

class GPSData(models.Model):
    user = models.ForeignKey(User, related_name='gpsdata', on_delete=models.CASCADE)
    geo_code = models.PointField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)