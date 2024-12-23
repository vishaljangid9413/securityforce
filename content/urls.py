from django.urls import path
from .views import *

urlpatterns = [
    path('api/faqs/', FAQListView.as_view(), name='faq-list'),
    path('api/faq/categories/', FAQView.as_view(), name='faq'),
]

'''Now, you can access the list API at /faqs/ and apply filtering using query parameters like ?category=<category_name> or ?question=<search_query>. Make sure you have the necessary packages installed (djangorestframework and django-filter).'''