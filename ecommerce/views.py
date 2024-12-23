from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Feature, Product, Subscription, ProductFeature
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse
from django.utils import timezone
    

# ** ORDER LIST API ** 
class OrderListView(generics.ListAPIView):
    queryset = Subscription.objects.all()    
    serializer_class = SubscriptionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'product', 'order_status', 'payment_mode',) 
    search_fields = ('user', 'product')


# ** ORDER API **
class OrderView(APIView):
    
    def get(self, request, user_id = None, format=None):
        user_obj = request.user

        if user_id:
            try:
                user_obj = User.objects.get(pk = user_id)
            except:
                return Response({'detail':'Enter a valid User Id'}, status= status.HTTP_404_NOT_FOUND)
        
        subscripiton_obj = Subscription.objects.filter(user = user_obj)
        if subscripiton_obj is None:
            return Response({'detail':"User does not have any subscripiton"}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SubscriptionSerializer(subscripiton_obj, many=True)
            return Response(serializer.data)
            
    def post(self, request, format=None):
        subscription_obj = Subscription.objects.filter(user = request.user).first()
        if subscription_obj is not None:
            return Response({'detail':'User Already Have a Plan'})
        else:
            try:
                product_obj = Product.objects.get(id = request.data['product_id'])
                request.data['product'] = product_obj.id
            except:
                return Response({'detail':'Enter a valid Product Id'}, status= status.HTTP_404_NOT_FOUND)
            
            request.data['user'] = request.user.id
            request.data['product'] = request.data['product_id']
            request.data['valid_till'] = (timezone.now() + timezone.timedelta(days=30)).strftime("%Y-%m-%d")

            serializer = SubscriptionPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                if 'transaction_status' in request.data and request.data['transaction_status'] == "Succesfull":
                    product_obj.sell_count += 1
                    product_obj.save()
                return Response(serializer.data)
            return Response({'detail':serializer.errors})
    
    def delete(self, request, user_id, subscription_id , format=None):
        if request.user.is_superadmin == True:
            try: 
                user_obj = User.objects.get(pk = user_id)
            except:
                return Response({'detail':'Enter a Valid User Id'}, status= status.HTTP_404_NOT_FOUND)

            try:
                obj = Subscription.objects.get(pk = subscription_id, user__id = user_id)
                obj.delete()
                return Response({'detail':'Order History Deleted Successfully'})
            except:
                return Response({'detail':'Enter a valid Subscription Id'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail':"Only SuperAdmin have this permission"})
            
    
    
    
    
class FeatureListCreateAPIView(APIView):
    def get(self, request, format=None):
        features = Feature.objects.all()
        serializer = FeatureSerializer(features, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = FeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListCreateAPIView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeatureDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        feature = self.get_object(pk)
        serializer = FeatureSerializer(feature)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        feature = self.get_object(pk)
        serializer = FeatureSerializer(feature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        feature = self.get_object(pk)
        feature.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class CartListCreateView(generics.ListCreateAPIView):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
