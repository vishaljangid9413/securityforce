from django.urls import path
from .views import FeedView, FeedListView, ComplaintListView, ComplaintView, SOSListView, SOSView, ReportView

urlpatterns = [
    path('api/feedList/', FeedListView.as_view(), name='FeedListView'),
    path('api/feed/', FeedView.as_view(), name='FeedView'),
    path('api/feed/<str:user_id>/', FeedView.as_view(), name='FeedView'),
    path('api/complaintList/', ComplaintListView.as_view(), name='ComplaintListView'),
    path('api/complaint/', ComplaintView.as_view(), name='ComplaintView'),
    path('api/complaint/<str:user_id>/', ComplaintView.as_view(), name='ComplaintView'),
    path('api/sosList/', SOSListView.as_view(), name='SOSListView'),
    path('api/sos/', SOSView.as_view(), name='SOSView'),
    path('api/sos/<str:user_id>/', SOSView.as_view(), name='SOSView'),
    path('api/report/', ReportView.as_view(), name='tr[pty-data'),

]
