from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from business.models import BusinessSite
from business.serializers import *
from django.shortcuts import HttpResponse
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .filters import DutyLogFilter
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon


class DutyLogListCreateAPIView(ListCreateAPIView):
    serializer_class = DutyLogSerializer
    queryset = DutyLog.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = DutyLogFilter

class RouteLogListCreateAPIView(ModelViewSet):
    serializer_class = RouteLogSerializer 
    permission_classes = (IsAuthenticated,)   
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('user', 'date',)
    search_fields = ('user',)

    def get_queryset(self):
        queryset = RouteLog.objects.filter(user=self.request.user)
        return queryset

class DutyLogDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = DutyLogSerializer
    queryset = DutyLog.objects.all()

# Getting MY (OFFICER'S/USER's Assigned) Routes List
class FetchMyRoutes(APIView):
    permission_classes = (IsAuthenticated,)  

    def get(self, request, business_id=None, format=None):        
        officer = FieldOfficer.objects.get(user=request.user)
        print(f'officer.routes::  {officer.routes.all()}')
        serializer = FORoutesSerializer(officer.routes,many=True)
        return Response(serializer.data)


# ** ROUTE ASSIGN API **
class RouteAssignView(APIView):
    
    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                if request.data.get('user_id', None) != None:
                    user_obj = User.objects.get(pk = request.data['user_id'])
                    officer_obj = FieldOfficer.objects.get(user = user_obj)
                    request.data['fieldofficer'] = officer_obj.id
                elif request.data['fieldofficer']:
                    officer_obj = FieldOfficer.objects.get(id = request.data['fieldofficer'])
            except:
                return Response({'detail':'Enter a valid Officer Id'}, status=status.HTTP_404_NOT_FOUND)
            try:
                
                route_obj = Route.objects.get(id = request.data['route_id'], business = request.user.business.business.id)
                request.data['route'] = route_obj.id
            except:
                return Response({'detail':'Enter a valid Route Id'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = RouteAssignPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':f'{route_obj.name} assigned to {officer_obj}'},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, user_id, route_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                user_obj = User.objects.get(pk = user_id)
                officer_obj = FieldOfficer.objects.get(user = user_obj)
                route_obj = Route.objects.get(id = route_id)
                objects = FieldOfficerRoute.objects.get(route=route_obj, fieldofficer=officer_obj)
                objects.delete()

                return Response({'detail':f'Removed the {officer_obj} from the {route_obj.name}'},status=status.HTTP_200_OK)
            except:
                return Response({'detail':f"This action can't be completed, bacause {officer_obj} doesn't work on {route_obj.name}"},status=status.HTTP_404_NOT_FOUND)          
        else:
            return Response({'detail': 'User Does not have any registered business'}, status=status.HTTP_404_NOT_FOUND)
            

# ** SITE ASSIGN API **
class SiteAssignView(APIView):

    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                user_obj = User.objects.get(pk = request.data['user_id'])
                officer_obj = FieldOfficer.objects.get(user = user_obj)
                request.data['fieldofficer'] = officer_obj.id
            except:
                return Response({'detail':'Enter a valid Officer Id'}, status=status.HTTP_404_NOT_FOUND)
            try:
                site_obj = BusinessSite.objects.get(id = request.data['site_id'], business = request.user.business.business.id)
                request.data['site'] = site_obj.id
            except:
                return Response({'detail':'Enter a valid Site Id'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = SiteAssignPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':f'{site_obj.name} assigned to {officer_obj}'},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, user_id, site_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                user_obj = User.objects.get(pk = user_id)
                officer_obj = FieldOfficer.objects.get(user__id = user_obj.id)
                site_obj = BusinessSite.objects.get(id = site_id)
                objects = FieldOfficerSite.objects.get(site=site_obj, fieldofficer=officer_obj)
                objects.delete()
                return Response({'detail':f'Removed the {officer_obj} from the {site_obj.name}'},status=status.HTTP_200_OK)
            except:
                return Response({'detail':f"This action can't be completed, bacause {officer_obj} doesn't work on {site_obj.name}"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)


# ** DUTY LOG LIST API **
class DutyLogListView(generics.ListAPIView):
    queryset  = DutyLog.objects.all()
    serializer_class = DutyLogSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user','date')
    search_fields = ('user',)

class DutyStatusView(APIView):
    def get(self, request, format=None):
        try:
            duty =  DutyLog.objects.get(user=request.user, date=date.today())
            serializer = DutyLogBaseSerializer(duty, many=False)
            return Response(serializer.data)
        except DutyLog.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

# ** DUTY LOG API **
class DutyLogView(APIView):
    
    def get(self, request, user_id=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            user = request.user
            if user_id:                
                try:
                    log_objs = DutyLog.objects.filter(user__id = user_id)
                except:
                    return Response({'detail': 'Enter a valid User Id'}, status= status.HTTP_404_NOT_FOUND)
            else:
                log_objs = DutyLog.objects.filter(user = request.user)
            serializer = DutyLogSerializer(log_objs, many=True)
            
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)       

    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                today_date = datetime.now().strftime('%Y-%m-%d')
                # it gives an error that the queryset is immutable, so that's why we do this
                request.data._mutable=True
                request.data['user'] = request.user.id

                #Create Start Point instance from coordinates
                start_point_latitude = request.data.get('start_point_latitude', None)
                start_point_longitude = request.data.get('start_point_longitude',None)
                if start_point_latitude and start_point_longitude:
                    start_point = Point(float(start_point_longitude), float(start_point_latitude))
                    request.data['start_point'] = start_point

                # Create End Point instance from coordinates
                end_point_latitude = request.data.get('end_point_latitude', None)
                end_point_longitude = request.data.get('end_point_longitude', None)

                if end_point_latitude and end_point_longitude:
                    end_point = Point(float(end_point_longitude), float(end_point_latitude))
                    request.data['end_point'] = end_point

                dutylog_obj = DutyLog.objects.filter(user=request.user, date=today_date)

                if not dutylog_obj:                    
                    serializer = DutyLogPostSerializer(data = request.data)
                else:                    
                    serializer = DutyLogPostSerializer(dutylog_obj.first(), data = request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response({'detail':serializer.errors})
                # else:
                #     return Response({'detail':'Already have a duty log'},status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'details':str(e)})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)   

    def patch(self, request, user_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                log_obj = DutyLog.objects.get(user__id = user_id)
            except:
                return Response({'detail':'Enter a valid User Id'}, status= status.HTTP_404_NOT_FOUND)

            serializer = DutyLogSerializer(log_obj, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Log Updated Successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'detail':serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)   


# ** SITE VISIT DATA LIST API **
class SiteVisitDataListView(generics.ListAPIView):
    # queryset = SiteVisitData.objects.all()
    permission_classes = (IsAuthenticated,) 
    serializer_class = SiteVisitDataSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'site', 'date')
    search_fields = ('user', 'site')

    def get_queryset(self):
        queryset = SiteVisitData.objects.filter(user=self.request.user)
        return queryset

# ** SiteVisitData API **
class SiteVisitDataView(APIView):    

    def get(self, request, user=None, route=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            data = SiteVisitData.objects.all()            
            user = request.user.id if not user else user                
            visits = data.filter(user__id = user)
            if route:
                try:                    
                    sites = Route.objects.get(pk=route).sites.all()
                    visits = visits.filter(site__in=[site.site.id for site in sites])
                except Exception as e:                    
                    return Response({'detail': str(e)},status=status.HTTP_400_BAD_REQUEST)

            serializer = SiteVisitDataSerializer(visits, many=True)           
                    
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            request.data['user'] = request.user.id
            try:
                site_obj = BusinessSite.objects.get(id = request.data['site'], business = request.user.business.business)
                request.data['site'] = site_obj.id
            except:
                return Response({'detail':'Enter a valid Site Id'}, status = status.HTTP_404_NOT_FOUND)          

            serializer = SiteVisitDataPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Visit created successfully'},status=status.HTTP_200_OK)
            return Response({'detail':serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)       
    
    def patch(self, request, sitevisit_data_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                sitevisit_obj = SiteVisitData.objects.get(pk = sitevisit_data_id)
            except:
                return Response({'detail':'Enter a valid Id'}, status= status.HTTP_404_NOT_FOUND)
            serializer = SiteVisitDataPostSerializer(sitevisit_obj, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Visit Updated Successfully'},status=status.HTTP_200_OK)
            return Response({'detail':serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED) 

# ** CHECKPOINT VISIT DATA LIST API **
class CheckpointVisitDataListView(generics.ListAPIView):
    # queryset = CheckpointVisitData.objects.all()
    permission_classes = (IsAuthenticated,) 
    serializer_class = CheckpointVisitDataSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'date',)
    search_fields = ('user',)

    def get_queryset(self):
        queryset = SiteVisitData.objects.filter(user=self.request.user)
        return queryset

# ** CheckpointVisitData API **
class CheckpointVisitDataView(APIView):
    
    def get(self, request, user=None, site=None, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            data = CheckpointVisitData.objects.all()            
            user = request.user.id if not user else user                
            visits = data.filter(user__id = user)
            if site:
                try:                    
                    business_site = BusinessSite.objects.get(pk=site)
                    # checkpoints = business_site.checkpoints.all()
                    visits = visits.filter(checkpoint__business_site__in=site)
                except Exception as e:                    
                    return Response({'detail': str(e)},status=status.HTTP_400_BAD_REQUEST)

            serializer = CheckpointVisitDataSerializer(visits, many=True)                        
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)       
    
    def post(self, request, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            request.data['user'] = request.user.id
            try:
                site_obj = Checkpoint.objects.get(id = request.data['checkpoint'], business_site__business=request.user.business.business)                
            except:
                return Response({'detail':'Enter a valid Checkpoint Id'}, status = status.HTTP_404_NOT_FOUND)
           
            serializer = CheckpointVisitDataPostSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Checkpoint Log created successfully'},status=status.HTTP_200_OK)
            return Response({'detail':serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)       
    
    def patch(self, request, sitevisit_data_id, format=None):
        if hasattr(request.user, 'business') and request.user.business:
            try:
                sitevisit_obj = CheckpointVisitData.objects.get(pk = sitevisit_data_id)
            except:
                return Response({'detail':'Enter a valid Id'}, status= status.HTTP_404_NOT_FOUND)
            serializer = CheckpointVisitDataPostSerializer(sitevisit_obj, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Visit Updated Successfully'},status=status.HTTP_200_OK)
            return Response({'detail':serializer.errors})
        else:
            return Response({'detail': 'User Does not have any registered business'},status=status.HTTP_401_UNAUTHORIZED)