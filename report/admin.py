from django.contrib import admin
from .models import *

class FeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'checkpoint', 'timestamp', 'viewed')

class FeedImageAdmin(admin.ModelAdmin):
    list_display = ('feed', 'image','timestamp')

class FeedVideoAdmin(admin.ModelAdmin):
    list_display = ('feed', 'timestamp')

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'checkpoint', 'timestamp', 'viewed')

class ComplaintImageAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'timestamp')

class ComplaintVideoAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'timestamp')

class SOSAdmin(admin.ModelAdmin):
    list_display = ('user', 'checkpoint', 'timestamp', 'viewed')

class SOSImageAdmin(admin.ModelAdmin):
    list_display = ('sos', 'timestamp')

class SOSVideoAdmin(admin.ModelAdmin):
    list_display = ('sos', 'timestamp')




admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedImage, FeedImageAdmin)
admin.site.register(FeedVideo, FeedVideoAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(ComplaintImage, ComplaintImageAdmin)
admin.site.register(ComplaintVideo, ComplaintVideoAdmin)
admin.site.register(SOS, SOSAdmin)
admin.site.register(SOSImage, SOSImageAdmin)
admin.site.register(SOSVideo, SOSVideoAdmin)