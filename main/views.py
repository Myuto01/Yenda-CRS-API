from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from json import JSONDecodeError
from rest_framework import views, status, renderers
from .models import User, TripSchedule, Bus
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BusSerializer, TripScheduleSerializer
from .utils import generate_otp_for_user_from_session, generate_otp_for_new_number
from .permissions import AllowAnyPermission
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, APIException
#from django.core.exceptions import MultipleObjectsReturned
from rest_framework_simplejwt.authentication import JWTAuthentication


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
            return Response(validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusCreateView(APIView):
    def post(self, request):
        try:
            # Access the user associated with the request
            user = request.user
            
            # Create a new instance of Bus with the associated user
            serializer = BusSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)  # Associate the request's user with the Bus
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Return an error response with details of the exception
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TripScheduleCreateView(APIView):

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
