from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Feature)
admin.site.register(ProductFeature)
admin.site.register(Subscription)