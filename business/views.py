from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Client, Business, BusinessSite, Checkpoint, UserInBusiness, Route, SiteInRoute
from .serializers import (BusinessSerializer,
                          UserInBusinessBaseSerializer,
                          UserInBusinessSerializer,
                          UserInBusinessPostSerializer,
                          ClientSerializer,
                          ClientPostSerializer,
                          FieldOfficerPostSerializer,
                          ManagerFieldOfficerSerializer,
                          CheckpointSerializer,
                          CheckpointPostSerializer,
                          BusinessSiteSerializer,
                          BusinessSiteClientSerializer,
                          BusinessSitePostSerializer,
                          RouteWithSiteSerializer,
                          RouteSerializer,
                          RoutePostSerializer,
                          SiteInRouteSerializer,
                          SiteInRoutePostSerializer)
from officer.models import FieldOfficer, FieldOfficerRoute, FieldOfficerSite
from officer.serializers import FieldOfficerSerializer
from accounts.serializers import UserRegistrationSerializer, UserSerializer
from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.db import transaction
from .permissions import IsBusinessAdmin, IsManager
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
import json
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import User
from location.models import Location
from master.models import Shift
from django.db.models import Q
from location.serializers import LocationSerializer
from django.core import serializers
from itertools import groupby
from operator import itemgetter


# ** BUSINESS List API **
class BusinessListView(generics.ListAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'email',)
    search_fields = ('name',)


# ** BUSINESS API **
class BusinessView(APIView):
    def get_object(self, business_id):
        return get_object_or_404(Business, pk=business_id)

    def get(self, request, business_id=None, format=None):
        # Check if the user has a business attribute before accessing it
        if hasattr(request.user, 'business') and request.user.business:
            if business_id:
                business = self.get_object(business_id)
            else:
                business = get_object_or_404(Business, pk=request.user.business.business.id)
            serializer = BusinessSerializer(business)
            managers_list = UserInBusiness.objects.filter(business=request.user.business.business, role__in=["admin", "manager"])
            managerSerializer = UserInBusinessSerializer(managers_list, many=True)

            data = {
                "data": serializer.data,
                "managers_list": managerSerializer.data
            }

            return Response(data)
        else:
            return Response({'error': 'Business does not exist for the user.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        # Deserialize the incoming business data
        if hasattr(request.user, 'business'):
            return Response({'detail': 'User already have a business'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                with transaction.atomic():
                    serializer = BusinessSerializer(data=request.data)

                    if serializer.is_valid():
                        # Extract latitude and longitude from the request data
                        latitude = request.data.get('latitude')
                        longitude = request.data.get('longitude')
                        # Create the Point instance for geo_code
                        if latitude != 'undefined' and longitude != 'undefined':
                            geo_code = Point(float(longitude), float(latitude))
                            # Save the business instance
                            business = serializer.save(geo_code=geo_code)
                        else:
                            business = serializer.save()

                        # Get the currently logged-in user (assuming you're using authentication)
                        user = self.request.user

                        # Create a UserInBusiness instance for the user as admin
                        user_in_business = UserInBusiness.objects.create(
                            user=user,
                            business=business,
                            role='admin',
                            is_active=True
                        )

                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Handle other exceptions
                transaction.rollback()
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, business_id, format=None):
        business = self.get_object(business_id)
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_id, format=None):
        business = self.get_object(business_id)
        business.is_deleted = True
        business.save()
        return Response({'detail': "Business deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)


# ** CLIENT List API **
class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('agency', 'client',)
    search_fields = ('agency', 'client',)


# ** CLIENT API **
class ClientView(APIView):
    def get_object(self, business_id):
        return get_object_or_404(Business, pk=business_id)

    def get(self, request, business_id=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            request_id = request.user.business.id
            obj = UserInBusiness.objects.get(pk=request_id)
            if business_id:
                try:
                    clients = Client.objects.get(agency_id=obj.business.id, client_id=business_id)
                    serialiser = ClientSerializer(clients)
                except:
                    return Response({'detail': 'Client does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                clients = Client.objects.filter(agency_id=obj.business.id)
                serialiser = ClientSerializer(clients, many=True)

            return Response(serialiser.data)
        else:
            return Response({'detail': 'User Does not have any registered business'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        user_business = request.user.business
        if not user_business or not user_business.is_active:
            raise PermissionDenied("You cannot create a client without an active business.")

        agency_id = user_business.business.id
        client_id = request.data.get('client_id')
        user_id = request.data.get('user_id')
        new_client_data = request.data.get('new_client_data')
        admin_details = request.data.get('admin_details')

        if client_id:
            # If 'client_id' is provided, create a client relationship with an existing business
            try:
                client = Business.objects.get(
                    Q(id=client_id) | Q(registration_number=client_id))
                if client.is_agency:
                    return Response({'detail': 'Agency Cannot be added as an Client'}, status=status.HTTP_400_BAD_REQUEST)
            except Business.DoesNotExist:
                return Response({'detail': 'Client id is not valid'}, status=status.HTTP_400_BAD_REQUEST)

            clientSerializer = ClientPostSerializer(data={
                'agency': agency_id,
                'client': client.id,
                'started_date': request.data.get('started_date'),
                'end_date': request.data.get('end_date'),
                'is_active': request.data.get('is_active')
            })
            if clientSerializer.is_valid():
                admin_user = clientSerializer.save()
                return Response({'detail': 'Client registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(clientSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif new_client_data:
            # If 'new_client_data' is provided, create a new business/client and a client relationship
            if new_client_data.get('is_agency', False) == True:
                return Response({'detail': 'Agency Cannot be Added as an Client'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    businessSerializer = BusinessSerializer(
                        data=new_client_data)
                    if businessSerializer.is_valid():
                        # Extract latitude and longitude from the request data
                        latitude = new_client_data.get('latitude')
                        longitude = new_client_data.get('longitude')
                        if latitude != 'undefined' and longitude != 'undefined':
                            # Create the Point instance for geo_code
                            geo_code = Point(float(longitude), float(latitude))
                            # Save the business instance
                            new_client = businessSerializer.save(
                                geo_code=geo_code)
                        else:
                            new_client = businessSerializer.save()
                    else:
                        return Response(businessSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    # ... Create admin user, Business, UserInBusiness instances ...
                    if user_id:
                        admin_user = User.objects.filter(Q(email=user_id) | Q(mobile=user_id)).first()
                        if hasattr(admin_user, 'business'):
                            raise Exception({'Detail': 'User is already with different business, please enter a different user\'s detail'})
                    else:
                        # Create an admin user for the new client
                        userSerializer = UserRegistrationSerializer(data=admin_details)
                        if userSerializer.is_valid():
                            admin_user = userSerializer.save()
                        else:
                            if "unique" in str(userSerializer.errors):
                                try:
                                    admin_user = User.objects.get(Q(email=admin_details['email'] | Q(mobile=admin_details['mobile'])))
                                    if hasattr(admin_user, 'business'):
                                        raise Exception(
                                            {'Detail': 'User is already with different business, please enter a different user\'s detail'})
                                except:
                                    raise Exception(
                                        {'detail': userSerializer.errors})

                    # Create a UserInBusiness instance for the admin user and new client
                    user_in_business = UserInBusiness.objects.create(
                        user=admin_user,
                        business=new_client,
                        role='admin',  # Set the role as admin
                        is_active=True
                    )

                    clientSerializer = ClientPostSerializer(data={
                        'agency': agency_id,
                        'client': new_client.id,
                        'started_date': request.data.get('started_date'),
                        'end_date': request.data.get('end_date'),
                        'is_active': request.data.get('is_active')
                    })

                    if clientSerializer.is_valid():
                        client = clientSerializer.save()                        
                        return Response(ClientSerializer(client).data)
                    else:
                        return Response(clientSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                # Handle other exceptions
                transaction.rollback()
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, business_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            request_id = request.user.business.id
            obj = UserInBusiness.objects.get(pk=request_id)
            try:
                latitude = request.data.get('latitude')
                longitude = request.data.get('longitude')
                if latitude != 'undefined' and longitude != 'undefined':
                    # Create the Point instance for geo_code
                    geo_code = Point(float(longitude), float(latitude))
                    request.data["geo_code"] = geo_code

                client = Client.objects.get(agency_id=obj.business.id, client_id=business_id)
                serialiser = ClientSerializer(client, data=request.data, partial=True)
                if serialiser.is_valid():
                    serialiser.save()   
                else:
                    return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)                
               
                bus_id = self.get_object(business_id)
                businessSer = BusinessSerializer(bus_id, data=request.data, partial=True)

                if businessSer.is_valid():                    
                    businessSer.save()                   
                else:
                    return Response(businessSer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                return Response(serialiser.data)
            except Client.DoesNotExist:
                return Response({'detail': 'Client does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User does not have any registered business'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, business_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            request_id = request.user.business.id
            obj = UserInBusiness.objects.get(pk=request_id)
            try:
                client = Client.objects.get(
                    agency_id=obj.business.id, client_id=business_id)
                client.is_active = False
                # business = Business.objects.get(pk=client.client.id)
                # business.is_deleted = True
                return Response({'detail': 'Client Deleted Successfully'},status=status.HTTP_200_OK)
            except:
                return Response({'detail': 'Client does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)


# ** SITE List API **
class SiteListView(generics.ListAPIView):
    queryset = BusinessSite.objects.all()
    serializer_class = BusinessSiteClientSerializer
    # serializer_class = BusinessSiteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'business',)
    search_fields = ('name', 'business',)


# ** SITE API **
class SiteView(APIView):
    # permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]
    permission_classes = [IsAuthenticated]

    def get(self, request, client_id=None, site_id=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            business_id = request.user.business.business.id
            if client_id:
                try:
                    sites = BusinessSite.objects.filter(business__id=client_id)
                    if site_id:
                        site = sites.filter(pk=site_id)
                        serializer = BusinessSiteSerializer(site, many=True)
                    else:
                        serializer = BusinessSiteSerializer(sites, many=True)
                    return Response(serializer.data)
                except:
                    return Response({'detail': 'Enter a Valid site Id'}, status=status.HTTP_404_NOT_FOUND)
            elif site_id:
                try:
                    sites = BusinessSite.objects.get(pk=site_id)
                    serializer = BusinessSiteSerializer(sites)
                    return Response(serializer.data)
                except BusinessSite.DoesNotExist as e:
                    return Response({'details':'Site not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                if request.user.business.business.is_agency:
                    client_obj = Client.objects.filter(agency__id=business_id)
                    business_site = BusinessSite.objects.filter(
                        business__id=business_id).first()
                    sites = []
                    sites.append(business_site)
                    for obj in client_obj:
                        site_objects = BusinessSite.objects.filter(
                            business=obj.client)
                        for site in site_objects:
                            sites.append(site)
                else:
                    sites = BusinessSite.objects.filter(
                        business__id=business_id)
                serializer = BusinessSiteSerializer(sites, many=True)
                return Response(serializer.data)
        else:
            return Response({'detail': 'User Does not have any registered business'})

    def post(self, request, format=None):
        
        if hasattr(request.user, 'business') and (request.user.business or request.user.business.is_agency):                    
            if request.user.business.role != "admin":
                return Response({'detail': 'Only Admin have the required permissions!'})

            # Extract latitude and longitude from request data
            latitude = request.data.pop('latitude', None)
            longitude = request.data.pop('longitude', None)

            # Create a Point object if latitude and longitude are provided
            if latitude is not None and longitude is not None:
                request.data['geo_code'] = Point(float(longitude), float(latitude))

            # Extract coordinates from request data
            coordinates = request.data.pop('area', None)

            # Create a Polygon object if coordinates are provided
            if coordinates:
                arr = [list(item.values()) for item in coordinates]                
                try:
                    request.data['area'] = Polygon(arr)
                except Exception as e:
                    print(str(e))
                
            # Now, create the serializer and instance as shown before
            site_serializer = BusinessSitePostSerializer(data=request.data)

            if site_serializer.is_valid():
                site_obj = site_serializer.save()
                return Response(BusinessSiteSerializer(site_obj).data)
            else:
                return Response(site_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User Does not have any registered business'})

    def patch(self, request, site_id, format=None):
        if hasattr(request.user, 'business') and (request.user.business or request.user.business.is_agency):                    
            if request.user.business.role != "admin":
                return Response({'detail': 'Only Admin have the required permissions!'})
           
            try:
                site_obj = BusinessSite.objects.get(pk=site_id)
            except:
                return Response({'detail': 'Please Enter a valid site id'}, status=status.HTTP_404_NOT_FOUND)
            

            # Extract latitude and longitude from request data
            latitude = request.data.pop('latitude', None)
            longitude = request.data.pop('longitude', None)

            # Create a Point object if latitude and longitude are provided
            if latitude is not None and longitude is not None:                
                request.data['geo_code'] = Point(float(longitude), float(latitude))

            # Extract coordinates from request data
            coordinates = request.data.pop('area', None)

            # Create a Polygon object if coordinates are provided
            if coordinates:
                arr = [[float(value) for value in item.values()] for item in coordinates]                
                try:                    
                    request.data['area'] = Polygon(arr)
                except Exception as e:
                    print(str(e))

            # Now, create the serializer and instance as shown before
            site_serializer = BusinessSitePostSerializer(site_obj, data=request.data, partial=True)

            if site_serializer.is_valid():
                site_serializer.save()
                return Response(BusinessSiteSerializer(site_obj).data)
            else:
                return Response(site_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User Does not have any registered business'})

    def delete(self, request, site_id, format=None):        
        
        if hasattr(request.user, 'business') and (request.user.business or request.user.business.is_agency):
            
            if request.user.business.role != "admin":
                return Response({'detail': 'Only Admin have the required permissions!'})
            
            try:
                site = BusinessSite.objects.get(pk=site_id)
                try:
                    client_obj = Client.objects.get(agency=request.user.business.business, client = site.business)
                    
                    site.delete()
                except:
                    return Response({'detail':'Entered site id do not belongs to any of your client.'}, status = status.HTTP_404_NOT_FOUND)
                                
                return Response({'detail': 'Site deleted successfully'})
            except:
                return Response({'detail': 'Please Enter a valid site id'}, status=status.HTTP_404_NOT_FOUND)

         
        #     business_id = request.user.business.business.id
        #     if request.user.business.business.is_agency:
        #         try:
        #             client_obj = Client.objects.get(agency=business_id, client = client_id)
        #         except:
        #             return Response({'detail':'Enter a valid client Id'}, status = status.HTTP_404_NOT_FOUND)

        #         try:
        #             site = BusinessSite.objects.get(id=site_id,business=client_obj.client)
        #             site.delete()
        #             return Response({'detail': 'Site deleted successfully'})
        #         except:
        #             return Response({'detail': 'Please Enter a valid site id'}, status=status.HTTP_404_NOT_FOUND)
                
            #     business_site_id = [site.id for site in business_site]

            #     for obj in client_obj:
            #         site_objects = BusinessSite.objects.filter(business=obj.client)
            #         for site in site_objects:
            #             # to verify that this particular sites is under the agency
            #             if site.id == site_id or site_id in business_site_id:
            #                 site.delete()
            #                 return Response({'detail': 'Site deleted successfully'})
            #         return Response({'detail': 'Please Enter a valid site id'}, status=status.HTTP_404_NOT_FOUND)
            # else:
            #     try:
            #         site = BusinessSite.objects.get(business__id=business_id, pk=site_id)
            #         site.delete()
            #         return Response({'detail': 'Site deleted successfully'})
            #     except:
            #         return Response({'detail': 'Please Enter a valid site id'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business'})


# ** CHECKPOINT  List API **
class CheckpointListView(generics.ListAPIView):
    queryset = Checkpoint.objects.all()
    serializer_class = CheckpointSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'business_site',)
    search_fields = ('name', 'business_site',)

# ** CHECKPOINT API **
class CheckpointView(APIView):
    # permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]
    permission_classes = [IsAuthenticated]

    def get(self, request, site_id, checkpoint_id=None, format=None):
        try:
            if checkpoint_id:
                checkpoints = Checkpoint.objects.filter(
                    id=checkpoint_id, business_site__id=site_id)
            else:
                checkpoints = Checkpoint.objects.filter(
                    business_site__id=site_id)
            if checkpoints:
                serializer = CheckpointSerializer(checkpoints, many=True)
                print(serializer.data)
                # queryset_data = queryset.values('business_site', 'id', 'name', 'floor', 'is_active')  
                grouped_queryset = []
                site = None
                floor = None
                for item in serializer.data:                
                    site = item['business_site']
                    floor = item['floor']
                    
                    checkpoints = []
                    for newitem in serializer.data:
                        if newitem['floor'] == floor:
                            checkpoints.append(newitem)
                        grouped_queryset.append({
                            'business_site': site,
                            'floors': [
                                {
                                    "floor": floor,
                                    "checkpoints": checkpoints
                                }
                            ]
                        })
                # for key, group in groupby(serializer.data, key=itemgetter('business_site')):
                #     print(key, list(group))    
                #     grouped_queryset.append({
                #         'business_site': key,
                #         'checkpoints': list(group)
                #     })
                return Response(grouped_queryset if not site_id else grouped_queryset[0])
            return Response([])
        except Exception as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        # Preprocess data before creating the serializer instance
        site_id = request.data.get('site_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # Create a Point instance for geo_code
        geo_code = Point(longitude, latitude)

        try:
            # Fetch the BusinessSite instance
            business_site = BusinessSite.objects.get(id=site_id)
        except:
            return Response({'detail': 'Enter a valid site Id'}, status=status.HTTP_404_NOT_FOUND)

        # Update request.data with preprocessed values
        request.data['business_site'] = business_site.id
        request.data['geo_code'] = geo_code

        # Create the serializer instance
        serializer = CheckpointPostSerializer(data=request.data)

        if serializer.is_valid():
            checkpoint = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, checkpoint_id, format=None):
        try:
            checkpoint = Checkpoint.objects.get(pk=checkpoint_id)
        except:
            return Response({'detail': 'Enter a valid Checkpoint id'}, status=status.HTTP_404_NOT_FOUND)

        # Preprocess data before updating the serializer instance
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude and longitude:
            # Create a Point instance for geo_code
            geo_code = Point(longitude, latitude)

            # Update request.data with preprocessed values
            request.data['geo_code'] = geo_code

        serializer = CheckpointPostSerializer(
            checkpoint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': "Checkpoint updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, checkpoint_id, format=None):
        try:
            checkpoint = Checkpoint.objects.get(pk=checkpoint_id)
            checkpoint.delete()
            return Response({'detail': 'Checkpoint deleted successfully'})
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


# ** ROUTE List API **
class RouteListView(generics.ListAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'business',)
    search_fields = ('name', 'business',)

# ** ROUTE API **
class RouteView(APIView):

    def get(self, request, route_id=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            business = request.user.business.business
            if route_id:
                try:
                    route = Route.objects.get(pk=route_id, business=business)
                    serializer = RouteWithSiteSerializer(route)
                except:
                    return Response(({'detail': 'Please enter a valid Route Id'}), status=status.HTTP_404_NOT_FOUND)
            else:
                routes = Route.objects.filter(business=business)
                serializer = RouteWithSiteSerializer(routes, many=True)
            return Response(serializer.data)

        else:
            return Response({'detail': 'User Does not have any registered business'})

    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business.role == "admin":
            request.data['business'] = request.user.business.business.id
            serializer = RoutePostSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({'detail': serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business or user is not a admin'})

    def patch(self, request, route_id, format=None):
        if hasattr(request.user, 'business') and request.user.business.role == "admin":
            business_id = request.user.business.business.id
            try:
                route_obj = Route.objects.get(
                    pk=route_id, business__id=business_id)
                serializer = RoutePostSerializer(
                    route_obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'detail': 'Business Route updated successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'detail': serializer.errors})
            except:
                return Response({'detail': 'Please enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business or user is not a admin'})

    def delete(self, request, route_id, format=None):
        if hasattr(request.user, 'business') and request.user.business.role == "admin":
            business_id = request.user.business.business.id
            try:
                route_obj = Route.objects.get(
                    pk=route_id, business__id=business_id)
                route_obj.delete()
                return Response({'detail': 'Route has been deleted successfully'})
            except:
                return Response({'detail': 'Please enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business or user is not a admin'})


# ** FIELD OFFICER API **
class FieldOfficerView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin | IsManager)]

    def get(self, request, officer_id=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            business_id = request.user.business.business.id
            if officer_id:
                try:
                    officer = FieldOfficer.objects.get(pk=officer_id)
                    users_in_business = UserInBusiness.objects.get(business__id=business_id, user=officer.user)
                    serializer = UserInBusinessSerializer(users_in_business)
                except:
                    return Response({'detail': 'Please enter a valid user Id'}, status=status.HTTP_404_NOT_FOUND)
            else:
                if request.user.business.role == "manager":
                    users_in_business = UserInBusiness.objects.filter(business__id=business_id, role="field_officer")
                elif request.user.business.role == "admin":
                    users_in_business = UserInBusiness.objects.filter(business__id=business_id).exclude(role="admin")
                serializer = UserInBusinessSerializer(users_in_business, many=True)
            return Response(serializer.data)
        else:
            return Response({'detail': 'User Does not have any registered business'})

    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business and request.user.business.role == "admin":
            serializer = FieldOfficerPostSerializer(data=request.data, context={'business': request.user.business, 'user': request.user})

            if serializer.is_valid():
                data = serializer.save()
                obj = UserInBusiness.objects.get(user__field_officer__id = data['officer_id'])
                return Response(UserInBusinessSerializer(obj).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User does not have required permission'})

    def patch(self, request, officer_id, format=None):
        # if hasattr(request.user, 'business') and request.user.business and request.user.business.role == "admin":

        try:
            officer_obj = FieldOfficer.objects.get(pk=officer_id)
        except:
            return Response({'detail': 'Please enter a valid Officer Id'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                user_serializer = UserSerializer(officer_obj.user, data=request.data, partial=True)
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    raise Exception(user_serializer.errors)
                
                officer_serializer = FieldOfficerSerializer(officer_obj, data=request.data, partial=True)
                if officer_serializer.is_valid():
                    officer_serializer.save()
                else:
                    raise Exception(officer_serializer.errors)
                
                if request.data.get('role', None):
                    userInBusinessSerializer = UserInBusinessPostSerializer(officer_obj.user.business, data=request.data, partial=True)
                    if userInBusinessSerializer.is_valid():
                        userInBusinessSerializer.handle_manager(request, officer_obj.user.business, request.data)
                        userInBusinessSerializer.save()
                    else:
                        raise Exception(userInBusinessSerializer.errors)
                
                return Response(UserInBusinessSerializer(officer_obj.user.business).data)
            
        except Exception as e:
            transaction.rollback()
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({'detail': 'User does not have required permission'})
            
    def delete(self, request, officer_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            if request.user.business.role == "admin":
                try:
                    officer_obj = FieldOfficer.objects.get(pk=officer_id)
                    user_in_business = officer_obj.user.business
                    user_in_business.delete()
                    officer_obj.delete()
                    return Response({'detail': 'Successfully deleted'})
                except:
                    return Response({'detail': 'Please enter a valid officer id'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'detail': 'You do not have permission to do this action'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'detail': 'User Does not have any registered business'})


# ** SITE IN ROUTE List API **
class SiteInRouteListView(generics.ListAPIView):
    queryset = SiteInRoute.objects.all()
    serializer_class = SiteInRouteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('route', 'site',)
    search_fields = ('route', 'site',)


# ** SITE IN ROUTE API **
class SiteInRouteView(APIView):
    # permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]
    permission_classes = [IsAuthenticated]

    def get(self, request, route_id, format=None):
        try:
            route_obj = Route.objects.get(pk=route_id)
        except:
            return Response({'detail': 'Enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
        objects = SiteInRoute.objects.filter(route=route_obj)
        serializer = SiteInRouteSerializer(objects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            route_obj = Route.objects.get(pk=request.data['route_id'])
            request.data['route'] = route_obj.id
        except:
            return Response({'detail': 'Enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
        try:
            # Getting users own business to check if the site belongs to it's own business
            user_business = request.user.business.business
            #combining user's own business with its clients businesses to get all the sites that an agency is managing.
            business_list = [item.client for item in user_business.agencies.all()]
            #appending users business with other clients
            business_list.append(user_business)
            #Getting BusinessSites related to any business on the list
            site_obj = BusinessSite.objects.get(pk=request.data['site_id'], business__in=business_list)
            request.data['site'] = site_obj.id
        except:
            return Response({'detail': 'Enter a valid Site Id'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SiteInRoutePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': f'Successfully added the site to {route_obj.name}', "data": serializer.data})
        else:
            return Response(serializer.errors)

    def delete(self, request, route_id, site_id, format=None):
        try:
            obj = SiteInRoute.objects.get(route__id=route_id, site__id=site_id)
            obj.delete()
            return Response({'detail': f'Site sucessfully deleted from this route.'})
        except Exception as e:
            print(str(e))
            return Response({'detail': f"Invalid route_id or site_id"})
        
        # THIS CODE CAN BE DELETED AFTER DISCUSSION WITH VISHAL
        """
        try:
            route_obj = Route.objects.get(pk=route_id)
        except:
            return Response({'detail': 'Enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user_business = request.user.business.business
            #combining user's own business with its clients businesses to get all the sites that an agency is managing.
            business_list = [item.client for item in user_business.agencies.all()]
            #appending users business with other clients
            business_list.append(user_business)
            #Getting BusinessSites related to any business on the list
            site_obj = BusinessSite.objects.get(pk=site_id, business__in=business_list)
            # site_obj = BusinessSite.objects.get(pk=site_id, business=request.user.business.business)
        except:
            return Response({'detail': 'Enter a valid Site Id'}, status=status.HTTP_404_NOT_FOUND)
        try:
            obj = SiteInRoute.objects.get(route=route_obj, site=site_obj)
            obj.delete()
            return Response({'detail': f'{site_obj.name} Removed Succefully from {route_obj.name}'})
        except:
            return Response({'detail': f"Can't Complete this action, {site_obj.name} is not assigned to {route_obj.name}"}, status=status.HTTP_404_NOT_FOUND)
        """


# ** SITE IN ROUTE List API **
class AssignManagerListView(generics.ListAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = FieldOfficerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'manager',)
    search_fields = ('user', 'manager',)


# ** ASSIGN MANAGER API **
class AssignManagerView(APIView):

    def get(self, request, user_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            business_id = request.user.business.business.id
            try:
                officers = FieldOfficer.objects.filter(manager__id=user_id)
                obj = [off.user for off in officers]
                users_in_business = UserInBusiness.objects.filter(business__id=business_id, user__in=obj)
                serializer = UserInBusinessSerializer(users_in_business, many=True)
            except:
                return Response({'detail': 'Please enter a valid user Id'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data)
        else:
            return Response({'detail': 'User Does not have any registered business'})

    def patch(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business.role == 'admin':
            try:
                manager_obj = User.objects.get(pk=request.data['manager_id'])
                if not (manager_obj.business.role == "manager" or manager_obj.business.role == "admin"):
                    return Response({'detail': 'Given User is not a Manager'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'detail': 'Enter a valid Manager Id'}, status=status.HTTP_400_BAD_REQUEST)

            if type(request.data['officer_id']) == list:
                officer_lists = [user.user.field_officer for user in UserInBusiness.objects.filter(user__in = request.data['officer_id'], role = "field_officer")]
            else:
                officer_lists = [user.user.field_officer for user in UserInBusiness.objects.filter(user = request.data['officer_id'], role = "field_officer")]

            if officer_lists:
                for officer in officer_lists:
                    officer.manager = manager_obj
                    officer.save()
                return Response({'detail': f'{manager_obj.email} assigned to given Officer IDs as a Manager'})
            else:
                return Response({'detail': 'Enter valid Field Officer Id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User Does not have any registered business or not an Admin'})

    def delete(self, request, user_id, format=None):
        if hasattr(request.user, 'business') and request.user.business.role == 'admin':
            try:
                fieldOfficer_obj = FieldOfficer.objects.get(user=user_id)
            except:
                return Response({'detail': 'Enter a valid Field Officer Id'}, status=status.HTTP_400_BAD_REQUEST)

            fieldOfficer_obj.manager = None
            fieldOfficer_obj.save()
            return Response({'detail': 'Successfuly removed the manager.'})
        else:
            return Response({'detail': 'User Does not have any registered business or not an Admin'})


# ** REPLACE MANAGER API **
class ReplaceManagerView(APIView):
    
    def patch(self, request):
        if hasattr(request.user, 'business') and request.user.business.role == 'admin':
            try:
                manager_obj = User.objects.get(pk=request.data.get('manager_id'))
                alternate_manager_obj = User.objects.get(pk=request.data.get('alternate_manager_id'))
                if not (manager_obj.business.role == "manager" or manager_obj.business.role == "admin"):
                    return Response({'detail': 'Given User is not a Manager'}, status=status.HTTP_400_BAD_REQUEST)
                elif not (alternate_manager_obj.business.role == "mana0ger" or alternate_manager_obj.business.role == "admin"):
                    return Response({'detail': 'Given alternate User is not a Manager'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'Enter a valid Manager Id'}, status=status.HTTP_404_NOT_FOUND)

            if manager_obj.field_officers_manager.all():
                for officer in manager_obj.field_officers_manager.all():
                        officer.manager = alternate_manager_obj
                        officer.save()
                return Response({'detail': f"{manager_obj} is replaced by {alternate_manager_obj}"})
            else:
                return Response({'detail': 'Manager is not assigned to any field officer'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business or not an Admin'}, status=status.HTTP_404_NOT_FOUND)
        

# ** USER IN BUSINESS API **
class UserInBusinessView(APIView):

    def get(self, request, role="admin,field_officer,manager", format = None):
        try:            
            obj = UserInBusiness.objects.filter(business=request.user.business.business, role__in=role.split(","))
            serializer = UserInBusinessBaseSerializer(obj, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'detail':e})

    def patch(self, request, pk, format=None):
        user_in_business = get_object_or_404(UserInBusiness, pk=pk)
        new_role = request.data.get('role')

        if new_role in dict(UserInBusiness.ROLE_CHOICES):
            # Check if the current user's associated business has an admin role
            if not request.user.business.role == 'admin':
                return Response({'error': 'Only admins can change user roles.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the new role is 'admin' and if the user is the only admin
            if new_role != 'admin' and user_in_business.role == 'admin':
                admins_count = UserInBusiness.objects.filter(
                    business=user_in_business.business, role='admin').exclude(user=user_in_business.user).count()
                if admins_count == 0:
                    return Response({'error': 'Cannot change role. At least one admin is required.'}, status=status.HTTP_400_BAD_REQUEST)

            user_in_business.role = new_role
            user_in_business.save()
            return Response({'detail': 'User role updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)


class ManagerFieldOfficerListView(APIView):
    # Custom permission to check if user is business admin
    permission_classes = [IsBusinessAdmin]

    def get(self, request, format=None):
        business = request.user.business
        managers_and_field_officers = business.users.filter(
            role__in=['manager', 'field_officer'])
        serializer = ManagerFieldOfficerSerializer(
            managers_and_field_officers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FieldOfficerAddAPIView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]

    def post(self, request, format=None):
        serializer = FieldOfficerAddSerializer(data=request.data, context={
                                               'business': request.user.business})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Field officer added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessSiteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, businessSite_id, format=None):
        try:
            site = BusinessSite.objects.get(pk=businessSite_id)
        except BusinessSite.DoesNotExist as e:
            return Response({"details":"Business with this id does not exists."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = BusinessSitePostSerializer(site, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        received_data = request.data

        # Convert business_id to a Business instance
        business_id = received_data['business_id']

        # Create Point instance from coordinates
        latitude = received_data['latitude']
        longitude = received_data['longitude']
        geo_code = Point(longitude, latitude)

        # Convert location_id to a Location instance
        location_id = received_data['location_id']

        # Create Polygon instance using Polygon.from_bbox()
        bbox = (longitude - 0.01, latitude - 0.01,
                longitude + 0.01, latitude + 0.01)
        area = Polygon.from_bbox(bbox)

        schedule_id = received_data['schedule_id']
        schedule_list = {
            'Daily': 'daily',
            'Weekly': 'weekly',
            'Monthly': 'monthly',
            'Bi-Weekly': 'bi-weekly',
        }
        if schedule_id not in schedule_list:
            schedule_id = 'Daily'

        received_data['schedule'] = schedule_list[schedule_id]
        received_data['business'] = business_id
        received_data['geo_code'] = geo_code
        received_data['location'] = location_id
        received_data['area'] = area

        # Now, create the serializer and instance as shown before
        site_serializer = BusinessSitePostSerializer(data=received_data)

        if site_serializer.is_valid():
            site_serializer.save()
            return Response({'detail': 'Business site created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(site_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return


class BusinessSiteUpdateDeleteView(APIView):
    permission_classes = [IsBusinessAdmin]

    def get_object(self, pk):
        try:
            return BusinessSite.objects.get(pk=pk)
        except BusinessSite.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        site = self.get_object(pk)
        serializer = BusinessSiteSerializer(site)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        site = get_object_or_404(BusinessSite, pk=pk)

        # Preprocess data before updating the serializer instance
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        area_bbox = request.data.get('area_bbox')

        # Create a Point instance for geo_code
        geo_code = Point(longitude, latitude)

        # Update request.data with preprocessed values
        request.data['geo_code'] = geo_code
        request.data['area'] = Polygon.from_bbox(area_bbox)

        serializer = BusinessSiteSerializer(site, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Business site updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        site = self.get_object(pk)
        site.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteAssignmentView(APIView):
    permission_classes = [IsAuthenticated, (IsAdminUser | IsBusinessAdmin)]

    def post(self, request, pk, format=None):
        site = get_object_or_404(BusinessSite, pk=pk)
        serializer = RouteAssignmentSerializer(data=request.data)

        if serializer.is_valid():
            route_id = serializer.validated_data['route_id']
            # To add a site to a route
            route = get_object_or_404(Route, pk=route_id)
            route.sites.add(site)
            return Response({'detail': 'Site assigned to route successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
