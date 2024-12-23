from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feature, Product, Subscription, ProductFeature
from accounts.serializers import UserSerializer

User = get_user_model()


class FeatureSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feature
        fields = '__all__'
        
        
class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ('title', 'price', 'image', 'icon', 'sell_count')
      
        
class ProductFeaturedSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer()
    product = ProductSerializer()
    
    class Meta:
        model = ProductFeature
        fields = ('feature', 'product', 'is_active')


class SubscriptionUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile', 'photo', 'aadhar_number')
        

class SubscriptionSerializer(serializers.ModelSerializer):
    user = SubscriptionUserSerializer()
    product = ProductSerializer()
    
    class Meta:
        model = Subscription
        fields = ('user', 'product', 'purchase_time', 'valid_till', 'paid_amount', 'auto_renew', 'is_active', 'transaction_status', 'order_status', 'payment_mode', 'payment_txn_id')
        

class SubscriptionPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Subscription
        fields = '__all__'



# class FeatureSerializer(serializers.ModelSerializer):
  
#     class Meta:
#         model = Feature
#         fields = '__all__'

# class ProductSerializer(serializers.ModelSerializer):
  
#     class Meta:
#         model = Product
#         fields = '__all__'

# # class CartSerializer(serializers.ModelSerializer):
  
# #     class Meta:
# #         model = Cart
# #         fields = '__all__'

# class SubscriptionSerializer(serializers.ModelSerializer):
  
    # class Meta:
    #     model = Subscription
    #     fields = '__all__'


