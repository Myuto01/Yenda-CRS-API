from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from json import JSONDecodeError
from rest_framework import views, status, renderers, generics
from .models import User, TripSchedule, Bus, Feature, DriverDetails, Seat, Ticket
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, BusSerializer, TripScheduleSerializer, BusCreateSerializer, FeatureSerializer, CreateDriverDetailsSerializer, TripSubmissionSerializer, TicketSerializer
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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import  permission_classes

#Remove

def login_view(request):
    return render(request, 'login.html')

def home_view(request):
    return render(request, 'home.html')

def test_view(request): #Bus Creation  View
    return render(request, 'test.html')

def trip_create_view(request):
    return render(request, 'create_trip.html')

def create_driver_details(request):
    return render(request, 'create_driver_details.html')

def trip_search(request):
    return render(request, 'trip_search.html')

def trip_results_view(request):
    return render(request, 'trip_results.html')

def bus_details_view(request):
    return render(request, 'bus_details.html')

def enter_passenger_details_view(request):
    return render(request, 'enter_passenger_details.html')

def confirm_passenger_details_view(request):
    return render(request, 'details_confirmation_page.html')

def tickets_view(request):
    return render(request, 'tickets.html')

def profile_view(request):
    return render(request, 'profile.html')
    
def account_details_view(request):
    return render(request, 'account_details.html')

def qr_code_scanner_view(request):
    return render(request, 'qr_code_scanner.html')

def bus_list_view(request):
    return render(request, 'bus_list.html')

def edit_bus_view(request):
    return render(request, 'edit_bus.html')

def driver_list_view(request):
    return render(request, 'driver_list.html')

def driver_details_view(request):
    return render(request, 'driver_details.html')

class EditDriverDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve the driver_id from the request data
        driver_id = request.data.get('driver_id')

        # Check if driver_id is present
        if not driver_id:
            return JsonResponse({'error': 'Driver ID is missing from the data'}, status=400)

        # Retrieve the driver object from the database
        driver = get_object_or_404(DriverDetails, pk=driver_id)

        # Update driver attributes if the corresponding data is provided
        if 'driver_name' in request.data and request.data['driver_name']:
            driver.driver_name = request.data.get('driver_name')

        if 'phone_number' in request.data and request.data['phone_number']:
            driver.phone_number = request.data.get('phone_number')

        if 'nrc_number' in request.data and request.data['nrc_number']:
            driver.nrc_number = request.data.get('nrc_number')

        if 'license_number' in request.data and request.data['license_number']:
            driver.license_number = request.data.get('license_number')

        if 'passport_number' in request.data and request.data['passport_number']:
            driver.passport_number = request.data.get('passport_number')

        # Save the changes to the driver object
        driver.save()

        # Return a success response
        return JsonResponse({'success': True})

class EditDriverPicsDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve the driver_id from the request data
        driver_id = request.data.get('driver_id')

        # Check if driver_id is present
        if not driver_id:
            return JsonResponse({'error': 'Driver ID is missing from the data'}, status=400)

        # Retrieve the driver object from the database
        driver = get_object_or_404(DriverDetails, pk=driver_id)

        # Update driver attributes if the corresponding data is provided
        if 'license_image' in request.FILES:
            driver.license_image = request.FILES['license_image']

        if 'nrc_image' in request.FILES:
            driver.nrc_image = request.FILES['nrc_image']

        if 'passport_image' in request.FILES:
            driver.passport_image = request.FILES['passport_image']

        # Save the changes to the driver object
        driver.save()

        # Return a success response
        return JsonResponse({'success': True})


class DriverDetailsView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver_id = request.data.get('driver_id')  
        
        print("Driver", driver_id)

        if not driver_id:
            return Response({'error': 'Driver ID is required'}, status=400)

        try:
            # Retrieve the driver object from the database
            driver = DriverDetails.objects.get(pk=driver_id)
        except DriverDetails.DoesNotExist:
            # If the driver does not exist, raise a NotFound exception
            raise NotFound("Driver not found")

        # Serialize the driver object
        serializer = CreateDriverDetailsSerializer(driver)

        # Return the serialized data as a JSON response
        return Response(serializer.data)

##############################################################################

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
        
       # Include uploaded file data in the deserialized data dictionary if available
        if 'fileData' in request.FILES:
            deserialized_data['seat_picture'] = request.FILES['fileData']

        print("PASS")

        # Pass the combined data to the serializer
        serializer = BusCreateSerializer(data=deserialized_data)
        print('serializer:', serializer)

        if serializer.is_valid():

            number_plate = serializer.validated_data['number_plate']
            
            if Bus.objects.filter(number_plate=number_plate).exists():
                return Response({'error': 'Number plate already registered'}, status=400)

            user = request.user
            bus_type = serializer.validated_data['bus_type']
            total_seats = serializer.validated_data['total_seats']
            number_plate = serializer.validated_data['number_plate']
            status = serializer.validated_data['status']
            feature_names = serializer.validated_data.get('features', [])

            seat_picture = None

            # Check if seat_picture is provided and not empty
            if 'seat_picture' in serializer.validated_data and serializer.validated_data['seat_picture']:
                    seat_picture = serializer.validated_data['seat_picture']
                # Process seat_picture if it's not empty
                # Your code for handling non-empty seat_picture goes here
            else:

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
                serialized_bus = BusCreateSerializer(bus)
                
            return Response(serialized_bus.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class EditBusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve the JSON data from the request body
        try:
            json_data = json.loads(request.data['jsonData'])
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Retrieve the bus_id from the JSON data
        bus_id = json_data.get('bus_id')

        # Check if bus_id is present
        if not bus_id:
            return JsonResponse({'error': 'Bus ID is missing from the data'}, status=400)

        # Retrieve the bus object from the database
        bus = get_object_or_404(Bus, pk=bus_id)

        # Update the bus object with the new data
        bus.bus_type = json_data.get('bus_type')
        bus.total_seats = json_data.get('total_seats')
        bus.number_plate = json_data.get('number_plate')
        bus.status = json_data.get('status')

        # If 'features' is a ManyToManyField or similar, handle it accordingly
        features = json_data.get('features', [])
        bus.features.set(features)

        if 'seat_picture' in request.FILES:
            seat_picture = request.FILES['seat_picture']
            bus.seat_picture.save(seat_picture.name, seat_picture, save=True)

        # Save the changes to the bus object
        bus.save()

        # Return a success response
        return JsonResponse({'success': True})

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
            features_data = request.data.get('features', [])  # Assuming features is a list of feature names or identifiers

            # Find or create the corresponding bus instance
            bus, created = Bus.objects.get_or_create(
                bus_type=bus_type,
                number_plate=number_plate,
                total_seats=total_seats,
            )

            # Create or update features associated with the bus
            features_objects = []
            for feature_name in features_data:
                feature_obj, _ = Feature.objects.get_or_create(name=feature_name)
                features_objects.append(feature_obj)

            # Update the features associated with the bus instance
            bus.features.set(features_objects)

            # Save the bus instance
            bus.save()

            # Create the new trip schedule instance
            trip_schedule = TripSchedule.objects.create(
                user=user,
                bus=bus,
                origin=request.data.get('origin', ''),
                destination=request.data.get('destination', ''),
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

    authentication_classes = []  
    permission_classes = []

    def get(self, request):
        # Extract search parameters from the request
        origin = request.query_params.get('origin')
        print('Origin :', origin)

        destination = request.query_params.get('destination')
        print('destination :', destination)

        date = request.query_params.get('date')  
        print('date :', date)

        # Filter trip details based on search criteria
        trips = TripSchedule.objects.filter(
            origin=origin,
            destination=destination,
            departure_date=date
        )

        # Serialize the filtered trip details
        serializer = TripScheduleSerializer(trips, many=True)
        print('serializer :', serializer)

        data_response = serializer.data
        print('Response:', data_response)
        # Return the serialized trip details in the response
        return Response(data_response)

class BusDetailsView(APIView):
    
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id)
            booked_seats = Seat.objects.filter(bus=bus, is_booked=True).count()
            booked_seat_numbers = list(Seat.objects.filter(bus=bus, is_booked=True).values_list('seat_number', flat=True))
            available_seats = bus.total_seats - booked_seats

            bus_data = {
                'bus': BusSerializer(bus).data,
                'available_seats': available_seats,
                'booked_seats': booked_seat_numbers
            }
            return Response(bus_data, status=status.HTTP_200_OK)
        except Bus.DoesNotExist:
            return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)


class FeatureListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FeatureSerializer

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


class BusListView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming YourModel has a ForeignKey to the User model
        queryset = Bus.objects.filter(user=request.user)  # Filter objects for the current user
        serializer = BusSerializer(queryset, many=True)
        return Response(serializer.data)

class CreateDriverDetailsAPIView(APIView):
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
        
        # Include uploaded file data in the deserialized data dictionary if available
        if 'license_image' in request.FILES:
            license_image_file = request.FILES['license_image']
            deserialized_data['license_image'] = license_image_file
            print("License Image File:", license_image_file)

        if 'nrc_image' in request.FILES:
            nrc_image_file = request.FILES['nrc_image']
            deserialized_data['nrc_image'] = nrc_image_file
            print("NRC Image File:", nrc_image_file)

        if 'passport_image' in request.FILES:
            passport_image_file = request.FILES['passport_image']
            deserialized_data['passport_image'] = passport_image_file
            print("Passport Image File:", passport_image_file)

        print("PASS")

        # Pass the combined data to the serializer
        serializer = CreateDriverDetailsSerializer(data=deserialized_data)
        print('serializer:', serializer)

        if serializer.is_valid():
            user = request.user
            driver_name = serializer.validated_data['driver_name']
            print("driver_name:", driver_name)
            license_number = serializer.validated_data['license_number']
            nrc_number = serializer.validated_data['nrc_number']
            phone_number = serializer.validated_data['phone_number']
            passport_number = serializer.validated_data.get('passport_number')
            print('passport_number:', passport_number)

            license_image = None
            nrc_image = None  
            passport_image = None

            # Check if any image is provided and not empty
            if 'license_image' in serializer.validated_data and serializer.validated_data['license_image']:
                license_image = serializer.validated_data['license_image']
                print("license_image", license_image)

            if 'nrc_image' in serializer.validated_data and serializer.validated_data['nrc_image']:
                nrc_image = serializer.validated_data['nrc_image']
                print("nrc_image", nrc_image)

            if 'passport_image' in serializer.validated_data and serializer.validated_data['passport_image']:
                passport_image = serializer.validated_data['passport_image']
                print("passport_image", passport_image)

            # Create or get the DriverDetails object
            driver, driver_created = DriverDetails.objects.get_or_create(
                driver_name=driver_name,
                license_number=license_number, 
                nrc_number=nrc_number, 
                phone_number=phone_number, 
                passport_number=passport_number,
                license_image=license_image,
                nrc_image=nrc_image,
                passport_image=passport_image,     
                user=user
            )

            # Serialize the driver instance with the updated features
            serialized_driver_details = CreateDriverDetailsSerializer(driver)
            
            return Response(serialized_driver_details.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverListView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming YourModel has a ForeignKey to the User model
        queryset = DriverDetails.objects.filter(user=request.user)  # Filter objects for the current user
        serializer = CreateDriverDetailsSerializer(queryset, many=True)
        return Response(serializer.data)

class TripSubmissionAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        data = request.data
        
        # Print original data
        print("Original data:", data)
        
        # Remove brackets and quotation marks from the data
        cleaned_data = {}
        for key, value in data.items():
            print(f"Processing {key}: {value}")
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                # Strip off brackets and quotation marks
                cleaned_value = [v.replace("[", "").replace("]", "").replace("'", "").replace('"', '') for v in value]
                print(f"Stripped {key}: {value} -> {cleaned_value}")
                cleaned_data[key] = cleaned_value
            else:
                cleaned_data[key] = value
        
        serializer = TripSubmissionSerializer(data=cleaned_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TicketDetailsAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        buyer_user_id = request.GET.get('buyer_user_id')
        ticket_details_for_user = Ticket.objects.filter(buyer_user_id=buyer_user_id, active=True)
        serializer = TicketSerializer(ticket_details_for_user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateTicketActiveStatus(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ticket_id = request.data.get('ticket_id')  
        print('Ticket Id:', ticket_id)
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.active = False 
            ticket.save()
            print('Done')
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            print('Failed')
            return Response({'success': False, 'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

class InactiveTicketDetailsAPIView(APIView):
        
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        buyer_user_id = request.GET.get('buyer_user_id')
        ticket_details_for_user = Ticket.objects.filter(buyer_user_id=buyer_user_id, active=False)
        serializer = TicketSerializer(ticket_details_for_user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyTicket(APIView):
    
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Extract QR code data from the request
        qr_data = request.data.get('qr_data')
        print("qr_data:", qr_data)

        # Validate and verify ticket based on QR code data
        try:
            ticket_details = {}
            for item in qr_data.split(', '):
                print("Splitting item:", item)
                try:
                    key, value = item.split(': ', 1)  # Split only once
                    print("Extracted key:", key)
                    print("Extracted value:", value)
                    
                    # Extract passenger name and seat number
                    if key == 'Passenger Name':
                        # Leave square brackets intact
                        value = value.strip()
                    elif key == 'Seat Number':
                        # Leave square brackets intact
                        value = value.strip()
                    ticket_details[key] = value
                except ValueError:
                    # Skip elements that cannot be split into key and value
                    print("Skipping element:", item)
                    continue

            # Query the Ticket model based on extracted data
            ticket = Ticket.objects.filter(
                trip_id=ticket_details.get('Trip_id'),
                bus_id=ticket_details.get('Bus_id'),
                passenger_name=ticket_details.get('Passenger Name'),
                seat_number=ticket_details.get('Seat Number')
            ).first()

            if ticket:
                # Ticket found, prepare response data
                response_data = {
                    "status": "success",
                    "ticket_details": {
                        "passenger_name": ticket.passenger_name,
                        "passenger_phonenumber": ticket.passenger_phonenumber,
                        "passenger_email": ticket.passenger_email,
                        "seat_number": ticket.seat_number,
                        "confirmed": ticket.confirmed,
                        # Add bus details
                        "bus_details": {
                            "bus_id": ticket.bus.id,
                            "Number Plate": ticket.bus.number_plate,
                            # Add more bus details as needed
                        }
                    }
                }
                return Response(response_data)
            else:
                # Ticket not found
                return Response({"status": "error", "message": "Ticket not found"})
        except Exception as e:
            print("Error occurred during QR code processing:", e)
            return Response({"status": "error", "message": "Error processing QR code"})

"""
class TicketDetailsAPIView(APIView):
    
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        buyer_user_id = request.GET.get('buyer_user_id')
        ticket_details_for_user = Ticket.objects.filter(buyer_user_id=buyer_user_id).first()
        serializer = TicketSerializer(ticket_details_for_user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
"""