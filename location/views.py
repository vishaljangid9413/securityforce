from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .models import *
from .serializers import LocationSerializer
import requests
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

# Create your views here.


class zipcodeLookup(APIView):

    def get(self, request, location=None, format=None):
        try:
            queryset = Zipcode.objects.get(pk=location)
            serializer = LocationSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise NotFound('Zipcode not found')

    def post(self, request, *args, **kwargs):
        try:
            zipcode = request.data.get('zipcode')
            # print(request.data)
            # Replace with your actual API key
            api_key = 'AIzaSyCAjhs0NAgTDjOoN3_kDiaK96YZXZ01XpY'

            url = f'https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={api_key}'
            response = requests.get(url)
            data = response.json()

            # Extract city, state, and country from the API response
            results = data.get('results', [])

            if results:
                address_components = results[0].get('address_components', [])
                city = next(
                    (comp['long_name'] for comp in address_components if 'locality' in comp['types']), None)
                state = next(
                    (comp['long_name'] for comp in address_components if 'administrative_area_level_1' in comp['types']), None)
                state_short = next(
                    (comp['short_name'] for comp in address_components if 'administrative_area_level_1' in comp['types']), None)
                country = next(
                    (comp['long_name'] for comp in address_components if 'country' in comp['types']), None)
                country_short = next(
                    (comp['short_name'] for comp in address_components if 'country' in comp['types']), None)

                country_obj, c_created = Country.objects.get_or_create(
                    name=country, short_name=country_short)
                state_obj, s_created = State.objects.get_or_create(
                    country=country_obj, name=state if state else country, short_name=state_short if state else country_short)
                city_obj, city_created = City.objects.get_or_create(
                    state=state_obj, name=city)
                location_obj, l_created = Zipcode.objects.get_or_create(
                    city=city_obj, zipcode=zipcode)
            else:
                city, state, country = None, None, None

            # Return the extracted information as a JSON response
            return JsonResponse({
                'city': city,
                'state': state if state else country,
                'country': country,
                'location': location_obj.id
            },status=status.HTTP_201_CREATED)
        
        except requests.RequestException as e:
            return Response({"Error": "Failed to connect to the Geocoding API"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        except KeyError as e:
            return Response({"Error": "Invalid data received from the Geocoding API"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"Error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
