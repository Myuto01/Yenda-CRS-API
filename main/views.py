from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from json import JSONDecodeError
from rest_framework import views, status, renderers, generics
from .models import User, TripSchedule, Bus, Feature
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BusSerializer, TripScheduleSerializer, BusFeatureSerializer, FeatureSerializer
from .utils import generate_otp_for_user_from_session, generate_otp_for_new_number
from .permissions import AllowAnyPermission
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, APIException
#from django.core.exceptions import MultipleObjectsReturned
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from rest_framework.parsers import MultiPartParser

#Remove
def test_view(request):
    try:
        feature = Feature.objects.get(pk=35)
        print("Feature with PK 35 exists:", feature)
    except Feature.DoesNotExist:
        print("Feature with PK 35 does not exist")
    return render(request, 'test.html')

class RegistrationAPIView(APIView):
    
    permission_classes = [AllowAnyPermission]

    serializer_class = UserRegistrationSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Create user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    'message': 'User created successfully',
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    
    permission_classes = [AllowAnyPermission]

    def post(self, request):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            print("Validated Data:", validated_data)
            return Response(validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusCreateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        json_data = request.POST.get('jsonData')
        
        # Remove square brackets using strip()
        json_data_stripped = json_data.strip('[]')
        print("pass:", json_data_stripped)
       
        # Deserialize the JSON string into a Python dictionary
        try:
            deserialized_data = json.loads(json_data_stripped)
            print("deserialized_data:", deserialized_data)
        except json.JSONDecodeError as e:
            return Response({'error': 'Failed to decode JSON data'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Include uploaded file data in the deserialized data dictionary
        deserialized_data['seat_picture'] = request.FILES.get('fileData')

        # Pass the combined data to the serializer
        serializer = BusFeatureSerializer(data=deserialized_data)
        print('serializer:', serializer)

        if serializer.is_valid():
            user = request.user
            bus_type = serializer.validated_data['bus_type']
            print("Bus Type:", bus_type)
            total_seats = serializer.validated_data['total_seats']
            number_plate = serializer.validated_data['number_plate']
            status = serializer.validated_data['status']
            feature_names = serializer.validated_data.get('features', [])
            print('feature_names:', feature_names)
            
            seat_picture = serializer.validated_data['seat_picture'] 

            bus, bus_created = Bus.objects.get_or_create(
                bus_type=bus_type,
                total_seats=total_seats, 
                number_plate=number_plate, 
                status=status, 
                seat_picture=seat_picture,     
                user=user
            )

            print("Bus:", bus )

            print('feature_names:', feature_names)
            # Set the features for the bus
            bus.features.set(feature_names)
            print("pass")
            # Serialize the bus instance with the updated features
            serialized_bus = BusFeatureSerializer(bus)
            
            return Response(serialized_bus.data, status=201)
        else:
            return Response(serializer.errors, status=400)




class TripScheduleCreateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            user = request.user

            # Extract bus details from the request data
            bus_type = request.data.get('bus_type')
            number_plate = request.data.get('number_plate')
            total_seats = request.data.get('total_seats')
            features = request.data.get('features')
            
            # Find or create the corresponding bus instance
            bus, created = Bus.objects.get_or_create(
                bus_type=bus_type,
                number_plate=number_plate,
                defaults={
                    'total_seats': total_seats,
                    'features': features
                }
            )
            
            # Create the new trip schedule instance
            trip_schedule = TripSchedule.objects.create(
                user=user,
                bus=bus,
                origin=request.data.get('origin', ''),
                departure=request.data.get('departure', ''),
                departure_date=request.data.get('departure_date', None),
                departure_time=request.data.get('departure_time', None)
            )
            
            # Return the serialized data of the created trip schedule
            serializer = TripScheduleSerializer(trip_schedule)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # This has been commented out because I am going to make the number plate unique, so buses with the same informations will be rear.
        #except MultipleObjectsReturned as e:
            # Return an error response with a user-friendly message
            #error_message = "Multiple buses found with the same information. Please contact support for assistance."
            #return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
         
        except Exception as e:
            # Return an error response with details of the exception
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TripSearchView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract search parameters from the request
        origin = request.query_params.get('origin')
        departure = request.query_params.get('departure')
        date = request.query_params.get('date')  # Assuming the date format is 'YYYY-MM-DD'

        # Filter trip details based on search criteria
        trips = TripSchedule.objects.filter(
            origin=origin,
            departure=departure,
            departure_date=date
        )

        # Serialize the filtered trip details
        serializer = TripScheduleSerializer(trips, many=True)
        data_response = serializer.data
        print('Response:', data_response)
        # Return the serialized trip details in the response
        return Response(data_response)

class BusDetailsView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id)
            booked_seats = TripSchedule.objects.filter(bus=bus).count()
            available_seats = bus.total_seats - booked_seats
            bus_data = {
                'bus': BusSerializer(bus).data,
                'available_seats': available_seats
            }
            return Response(bus_data, status=status.HTTP_200_OK)
        except Bus.DoesNotExist:
            return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)


class FeatureCreateAPIView(APIView):
    def post(self, request):
        serializer = BusFeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FeatureListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BusFeatureSerializer

    def get_queryset(self):
        # Get the currently authenticated user
        user = self.request.user

        # Filter the queryset to retrieve features belonging to the user
        queryset = Feature.objects.filter(user=user)

        return queryset

class FeatureCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Include the user information in the data before saving
        data = request.data
        # Pass the request context to the serializer
        serializer = FeatureSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)