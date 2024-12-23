from django.urls import path
from .views import OrderView, OrderListView, FeatureListCreateAPIView, FeatureDetailAPIView, ProductListCreateAPIView,  SubscriptionListCreateView, SubscriptionDetailView

urlpatterns = [
    path('features/', FeatureListCreateAPIView.as_view(), name='feature-list-create'),
    path('features/<int:pk>/', FeatureDetailAPIView.as_view(), name='feature-detail'),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    # path('cart/', CartListCreateView.as_view(), name='cart-list'),
    # path('cart/<int:pk>/', CartDetailView.as_view(), name='cart-detail'),
    path('subscription/', SubscriptionListCreateView.as_view(), name='subscription-list'),
    path('subscription/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),


    path('api/orderList/', OrderListView.as_view(), name='subscription-list-detail'),
    path('api/order/', OrderView.as_view(), name='subscription-detail'),
    path('api/order/<str:user_id>/', OrderView.as_view(), name='subscription-detail'),
    path('api/order/<str:user_id>/<int:subscription_id>/', OrderView.as_view(), name='subscription-detail'),

]
