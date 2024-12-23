from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client', 'client_admin', 'agency', 'agency_admin', 'started_date','end_date','is_active',)
    search_fields = ('agency', 'client',)
    list_filter = ('is_active', )

    def agency_admin(self, obj):
        return UserInBusiness.objects.filter(business=obj.agency, role="admin").first().user
    agency_admin.short_description = 'Agency Admin' 
    
    def client_admin(self, obj):
        return UserInBusiness.objects.filter(business=obj.client, role="admin").first().user
    client_admin.short_description = 'Client Admin'

@admin.register(BusinessSite)
class BusinessSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business', "geo_code","area")
    search_fields = ('name', 'business',)
    # list_filter = ('is_active', )

@admin.register(UserInBusiness)
class UserInBusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'business', 'role', 'is_active')
    search_fields = ('user', 'business',)
    list_filter = ('is_active', )

@admin.register(SiteInRoute)
class SiteInRouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'site')
    search_fields = ('route', 'site',)
    # list_filter = ('is_active', )

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business', 'is_active')
    search_fields = ('name', 'business',)
    list_filter = ('is_active', )

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_agency', 'is_active', 'phone', 'email', 'is_deleted')
    search_fields = ('name', 'phone','email',)
    list_filter = ('is_active', 'is_deleted')

@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'floor', 'business_site', 'is_active')
    search_fields = ('name', 'business_site')
    list_filter = ('is_active',)

# admin.site.register(Business)
# admin.site.register(BusinessSite)
# admin.site.register(Route)
# admin.site.register(SiteInRoute)

# admin.site.register(Checkpoint)
# admin.site.register(Client)
# admin.site.register(UserInBusiness)