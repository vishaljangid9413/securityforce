from django.contrib import admin
from .models import FieldOfficer, DutyLog, RouteLog, FieldOfficerRoute, FieldOfficerSite, SiteVisitData, CheckpointVisitData

@admin.register(FieldOfficer)
class FieldOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'manager', 'shift')

@admin.register(DutyLog)
class DutyLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'kilometers')

@admin.register(RouteLog)
class RouteLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'route', 'start_time', 'end_time', 'date', 'kilometers', 'status')


@admin.register(SiteVisitData)
class SiteVisitDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'site', 'date', 'start_time', 'end_time')

@admin.register(FieldOfficerRoute)
class FieldOfficerRouteAdmin(admin.ModelAdmin):
    list_display = ('route', 'fieldofficer')

@admin.register(FieldOfficerSite)
class FieldOfficerSiteAdmin(admin.ModelAdmin):
    list_display = ('site', 'fieldofficer')

@admin.register(CheckpointVisitData)
class CheckpointVisitDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'checkpoint', 'start_time', 'end_time', 'date')

# admin.site.register(SiteVisitData, SiteVisitDataAdmin)
# admin.site.register(FieldOfficer)
# admin.site.register(FieldOfficerRoute)
# admin.site.register(FieldOfficerSite)
# admin.site.register(CheckpointVisitData)
# admin.site.register(DutyLog, DutyLogAdmin)
# admin.site.register(RouteLog, RouteLogAdmin)
