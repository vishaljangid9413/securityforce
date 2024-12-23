from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Feature(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class Product(models.Model):                            
    # OFFER_CHOICES = ( 
    #     ('1 Month', '1000'),
    #     ('3 Month', '2700'),
    #     ('6 Month', '5000'),
    #     ('12 Month', '9000'),
    # 

    title = models.CharField(max_length=100, blank=True, null=True)                 
    price = models.FloatField()
    # offer_price = models.CharField(max_length=100, choices=OFFER_CHOICES, default='1 Month')
    image = models.ImageField(null=True, blank=True, upload_to='images/ecommerce/features/images')
    icon = models.ImageField(null=True, blank=True, upload_to='images/ecommerce/features/icons')
    sell_count = models.IntegerField()

    def __str__(self):
        return f"{self.title}"


class ProductFeature(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='product_features')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_features')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('feature', 'product')

    def __str__(self):
        return f"{self.product} product has {self.feature} feature"


class Subscription(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subscribed_products')
    purchase_time = models.DateTimeField(auto_now_add=True)
    valid_till = models.DateField()
    paid_amount = models.FloatField()
    auto_renew = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    transaction_status = models.CharField(max_length=100, blank=True, null=True)
    order_status = models.CharField(max_length=100, blank=True, null=True)
    payment_mode = models.CharField(max_length=100, blank=True, null=True)
    payment_txn_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} has {self.product} Subscription plan"

         
# class Cart(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_product')
#     time = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.mobile}"

