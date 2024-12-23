from django.contrib import admin
from .models import *

class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'time')

class MessageToUserAdmin(admin.ModelAdmin):
    list_display = ('reciever', 'sender', 'message', 'is_read')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'time')

class NotificationToUserAdmin(admin.ModelAdmin):
    list_display = ('reciever', 'sender', 'notification', 'is_read')

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time')

class NewsletterToUserAdmin(admin.ModelAdmin):
    list_display = ('reciever', 'sender', 'newsletter', 'is_read')

class HelpQuesAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'date', 'time', 'category')


admin.site.register(Message, MessageAdmin)
admin.site.register(MessageToUser, MessageToUserAdmin)

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationToUser, NotificationToUserAdmin)

admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(NewsletterToUser, NewsletterToUserAdmin)

admin.site.register(HelpQues, HelpQuesAdmin)
