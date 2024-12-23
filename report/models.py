from django.db import models
from django.contrib.auth import get_user_model
from business.models import Checkpoint

User = get_user_model()


class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feeds')
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name='feeds')
    message = models.TextField(blank=True, null=True)
    voice_note = models.FileField(blank=True, null=True, upload_to='reports/checkpoint/voice')
    timestamp = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.checkpoint.name}"
    


class FeedImage(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(null=True, blank=True, upload_to='reports/checkpoint/images/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feed.checkpoint.name}"


class FeedVideo(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(null=True, blank=True, upload_to='reports/checkpoint/video/')
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.feed.checkpoint.name}" 
    
    
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name='complaints')
    message = models.TextField(blank=True, null=True)
    voice_note = models.FileField(blank=True, null=True, upload_to = 'reports/checkpoint/voice')
    timestamp = models.DateTimeField(auto_now_add = True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.checkpoint.name}"


class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(null=True, blank=True, upload_to = 'reports/checkpoint/images/')
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.complaint.checkpoint.name}"


class ComplaintVideo(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(null=True, blank=True, upload_to='reports/checkpoint/video/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.checkpoint.name}"
    
    
class SOS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos')
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name='sos')
    message = models.TextField(blank=True, null=True)
    voice_note = models.FileField(blank=True, null=True, upload_to = 'reports/checkpoint/voice')
    timestamp = models.DateTimeField(auto_now_add = True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.checkpoint.name}"


class SOSImage(models.Model):
    sos = models.ForeignKey(SOS, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(null=True, blank=True, upload_to = 'reports/checkpoint/images/')
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.sos.checkpoint.name}"


class SOSVideo(models.Model):
    sos = models.ForeignKey(SOS, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(null=True, blank=True, upload_to='reports/checkpoint/video/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sos.checkpoint.name}"