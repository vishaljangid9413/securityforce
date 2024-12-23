from django.urls import path
from .views import *

urlpatterns = [
    # path('api/logs/', DutyLogListCreateAPIView.as_view(), name='duty-log-list'),
    # path('api/logs/<int:pk>/', DutyLogDetailAPIView.as_view(), name='duty-log-detail'),
    path('api/routeassign/', RouteAssignView.as_view(), name='route-assign'),
    path('api/routeassign/<str:user_id>/<str:route_id>/', RouteAssignView.as_view(), name='route-assign'),
    
    path('api/siteassign/', SiteAssignView.as_view(), name='site-assign'),
    path('api/siteassign/<str:user_id>/<str:route_id>/', SiteAssignView.as_view(), name='site-assign'),
    
    path('api/routeLogs/', RouteLogListCreateAPIView.as_view({'get': 'list', 'post': 'create'}), name='route-logs'),
    path('api/routeLogs/<int:pk>/', RouteLogListCreateAPIView.as_view({'patch':'update', 'delete':'destroy'}), name='route-logs'),
    
    path('api/dutylogsList/', DutyLogListView.as_view(), name='duty-log-list'),
    path('api/duty_status/', DutyStatusView.as_view(), name='duty-logs'),
    path('api/dutylogs/', DutyLogView.as_view(), name='duty-logs'),
    path('api/dutylogs/<str:user_id>/', DutyLogView.as_view(), name='duty-log-detail'),
    
    path('api/sitevisitList/', SiteVisitDataListView.as_view(), name='site-visit-data-list'),
    path('api/sitevisit/', SiteVisitDataView.as_view(), name='site-visit-data'),
    path('api/sitevisit/<int:route>/', SiteVisitDataView.as_view(), name='site-visit-data'),
    path('api/sitevisit/', SiteVisitDataView.as_view(), name='site-visit-data'),
    path('api/sitevisit/<int:site_id>/', SiteVisitDataView.as_view(), name='site-visit-data'),
    path('api/sitevisit/update/<int:sitevisit_data_id>/', SiteVisitDataView.as_view(), name='site-visit-data'),
    
    path('api/checkpointvisitList/', CheckpointVisitDataListView.as_view(), name='checkpoint-visit-data-list'),
    path('api/checkpointvisit/', CheckpointVisitDataView.as_view(), name='checkpoint-visit-data'),
    path('api/checkpointvisit/<int:site>', CheckpointVisitDataView.as_view(), name='checkpoint-visit-data'),
    path('api/checkpointvisit/<int:checkpoint_id>/', CheckpointVisitDataView.as_view(), name='checkpoint-visit-data'),
    path('api/checkpointvisit/update/<int:checkpointvisit_data_id>/', CheckpointVisitDataView.as_view(), name='checkpoint-visit-data'),

    path('api/myroutes/', FetchMyRoutes.as_view(), name='myroutes'),    
]