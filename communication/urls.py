from django.urls import path
from .views import (
    MessageListView,
    MessageView,
    NewsletterListView,
    NewsletterView,
    NotificationListView,
    NotificationView,
    HelpQuesListView,
    HelpQuesView,
    
    
    MessageListCreateAPIView,
    MessageDetailAPIView,
    NewsletterListCreateAPIView,
    NewsletterDetailAPIView,
    NotificationListCreateAPIView,
    NotificationDetailAPIView,
    SchedulerListCreateView,
    SchedulerDetailView
)
from master.views import HelpCategoryView

urlpatterns = [
    path('api/messageList/', MessageListView.as_view(), name='messageList'),
    path('api/message/', MessageView.as_view(), name='message'),
    path('api/message/<int:message_id>/', MessageView.as_view(), name='message'),
    path('api/newsletterList/', NewsletterListView.as_view(), name='newsletterList'),
    path('api/newsletter/', NewsletterView.as_view(), name='newsletter'),
    path('api/newsletter/<int:newsletter_id>/', NewsletterView.as_view(), name='newsletter'),
    path('api/notificationList/', NotificationListView.as_view(), name='NotificationListView'),
    path('api/notification/', NotificationView.as_view(), name='NotificationView'),
    path('api/notification/<int:notification_id>/', NotificationView.as_view(), name='NotificationView'),
    path('api/helpList/', HelpQuesListView.as_view(), name='help_quesList'),
    path('api/help/', HelpQuesView.as_view(), name='help_ques'),
    path('api/helpcategory/', HelpCategoryView.as_view(), name='help_category'),


    # path('messages/', MessageListCreateAPIView.as_view(), name='message-list'),
    # path('messages/<int:pk>/', MessageDetailAPIView.as_view(), name='message-detail'),
    # path('newsletters/', NewsletterListCreateAPIView.as_view(), name='newsletter-list'),
    # path('newsletters/<int:pk>/', NewsletterDetailAPIView.as_view(), name='newsletter-detail'),
    # path('notifications/', NotificationListCreateAPIView.as_view(), name='notification-list'),
    # path('notifications/<int:pk>/', NotificationDetailAPIView.as_view(), name='notification-detail'),

    path('api/scheduler/', SchedulerListCreateView.as_view(), name='scheduler-list-create'),
    path('api/scheduler/<str:pk>/', SchedulerDetailView.as_view(), name='scheduler-detail'),
]
