from django.db import models
from master.models import HelpCategory
from django.contrib.auth import get_user_model
User = get_user_model()


class Message(models.Model):
    CATEGORY_CHOICES = (
        ('normal', 'Normal'),
        ('flash', 'Flash'),
        ('emergancy', 'Emergancy')
    )
    title = models.CharField(max_length=20)
    content = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='normal')

    def __str__(self):
        return str(self.title)


class MessageToUser(models.Model):
    reciever = models.ForeignKey(User, related_name="message_reciever", on_delete=models.CASCADE, null=True, blank=True) 
    sender = models.ForeignKey(User, related_name="message_sender", on_delete=models.CASCADE, null=True, blank=True) 
    message = models.ForeignKey(Message, related_name="message_to_user", on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.sender.email} sent a message to {self.reciever.email}"


class Newsletter(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    is_html = models.BooleanField(default=False, blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/newsletters/')
    video = models.FileField(blank=True, null=True, upload_to='videos/newsletters/')

    def __str__(self):
        return str(self.title)


class NewsletterToUser(models.Model):
    reciever = models.ForeignKey(User, related_name="newsletter_reciever", on_delete=models.CASCADE, null=True, blank=True) 
    sender = models.ForeignKey(User, related_name="newsletter_sender", on_delete=models.CASCADE, null=True, blank=True) 
    newsletter = models.ForeignKey(Newsletter, related_name="newsletter_to_user", on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.sender.email} sent a newsletter to {self.reciever.email}"


class Notification(models.Model):
    CATEGORY_CHOICES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('schedule', 'Schedule'),
        ('event', 'Event')
    )
    title = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='info')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/notifications/')
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)


class NotificationToUser(models.Model):
    reciever = models.ForeignKey(User, related_name="notification_reciever", on_delete=models.CASCADE, null=True, blank=True) 
    sender = models.ForeignKey(User, related_name="notification_sender", on_delete=models.CASCADE, null=True, blank=True) 
    notification = models.ForeignKey(Notification, related_name="notification_to_user", on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email} sent a notification to {self.reciever.email}"


class HelpQues(models.Model):
    question = models.CharField(max_length=400)
    answer = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    category = models.ForeignKey(HelpCategory, related_name="help_categories", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.question)


class Scheduler(models.Model):
    SCHEDULED_STATUS = (
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    scheduled_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=SCHEDULED_STATUS, default='scheduled')

    def __str__(self):
        return f"Sender: {self.sender}, Recipient: {self.recipient}, Status: {self.status}"
