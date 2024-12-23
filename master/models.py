from django.db import models

# Create your models here.
class Shift(models.Model):
    title = models.CharField(max_length=100, blank=False)
    start_time = models.TimeField() 
    end_time = models.TimeField()
    duration = models.IntegerField()

    def __str__(self):
        return f"{self.title}"  
    

class HelpCategory(models.Model):
    name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return str(self.name)