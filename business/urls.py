from django.urls import path
from .views import *

urlpatterns = [
    path('api/businessList/', BusinessListView.as_view(), name='businesslist'),
    path('api/business/', BusinessView.as_view(), name='business'),
    path('api/business/<int:business_id>/', BusinessView.as_view(), name='business'),

    path('api/clientList/', ClientListView.as_view(), name='clientlist'),
    path('api/client/', ClientView.as_view(), name='client'),
    path('api/client/<int:business_id>/', ClientView.as_view(), name='client'),

    path('api/siteList/', SiteListView.as_view(), name='sitelist'),
    path('api/site/', SiteView.as_view(), name='site'),
    path('api/site/<int:site_id>/', SiteView.as_view(), name='site'),
    path('api/site/<int:client_id>/<int:site_id>/', SiteView.as_view(), name='site'),
    path('api/site/update/<int:site_id>/', SiteView.as_view(), name='site'),

    path('api/checkpointList/', CheckpointListView.as_view(), name='checkpointlist'),
    path('api/checkpoint/', CheckpointView.as_view(), name='checkpoint'),
    path('api/checkpoint/update/<int:checkpoint_id>/', CheckpointView.as_view(), name='checkpoint'),
    path('api/checkpoint/<int:site_id>/<int:checkpoint_id>/', CheckpointView.as_view(), name='checkpoint'),
    path('api/checkpoint/<int:site_id>/', CheckpointView.as_view(), name='checkpoint'),
    
    path('api/routeList/', RouteListView.as_view(), name='routelist'),
    path('api/route/', RouteView.as_view(), name='route'),
    path('api/route/<int:route_id>/', RouteView.as_view(), name='route'),

    path('api/officer/', FieldOfficerView.as_view(), name='officer'),
    path('api/officer/<int:officer_id>/', FieldOfficerView.as_view(), name='officer'),

    path('api/siteinrouteList/', SiteInRouteListView.as_view(), name='SiteInRouteList'),
    path('api/siteinroute/', SiteInRouteView.as_view(), name='SiteInRouteView'),
    path('api/siteinroute/<int:route_id>/', SiteInRouteView.as_view(), name='SiteInRouteView'),
    path('api/siteinroute/<int:route_id>/<int:site_id>/', SiteInRouteView.as_view(), name='SiteInRouteView'),

    path('api/assignManagerList/', AssignManagerListView.as_view(), name='assignManagerList'),
    path('api/assignManager/', AssignManagerView.as_view(), name='assignManager'),
    path('api/assignManager/<str:user_id>/', AssignManagerView.as_view(), name='assignManager'),
    path('api/replaceManager/', ReplaceManagerView.as_view(), name='assignManager'),

    path('api/userinbusiness/', UserInBusinessView.as_view(), name='UserRole'),
    path('api/userinbusiness/<str:role>/', UserInBusinessView.as_view(), name='UserRole'),
    path('api/fieldOfficer/', FieldOfficerAddAPIView.as_view(), name='field_officer'),
    # path('api/client/', ClientCreateView.as_view(), name='client'),
    path('api/business-officers-list/', ManagerFieldOfficerListView.as_view(), name='managers-field-officers'),
    path('api/business-site/create/', BusinessSiteView.as_view(), name='business-site-create'),
    path('api/business-site/<int:businessSite_id>/', BusinessSiteView.as_view(), name='business-site-assign-route'),
    path('api/business-site/<int:pk>/', BusinessSiteUpdateDeleteView.as_view(), name='business-site-detail'),
    path('api/business-site/<int:pk>/assign-route/', RouteAssignmentView.as_view(), name='business-site-assign-route'),    
    
]
