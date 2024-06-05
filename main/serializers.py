# serializers.py
from rest_framework import serializers
from main.models import User, Bus, TripSchedule, Feature,  DriverDetails, Ticket, Seat
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import  authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files import File

#chamge extra keyword arguments and log in serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = [
            "company_name",
            "contact_person",
            "email",
            "phone_number",
            "business_licence_number",
            "password",
            "password2"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'error_messages': {'required': 'Password is required'}},
            'phone_number': {'error_messages': {'unique': 'phone_number is already taken'}}
        }

    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.pop('password2')
        if password != password2:
            raise serializer.ValidationError("Password and Confirm Password Does not match")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Hash the password
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField( required=True)  
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials. Please try again.")

        user_tokens = user.tokens()
        access_token = user_tokens.get('access')
        refresh_token = user_tokens.get('refresh')

        validated_data = {
            'email': email,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return validated_data

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['name']

class BusSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    booked_seats_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = [ 
            'id',
            'bus_type',
            'total_seats',
            'number_plate',
            'features', 
            'status', 
            'seat_picture',
            'booked_seats_count' 
        ]
    
    def get_booked_seats_count(self, bus):
        # Get the count of booked seats for the given bus
        return Seat.objects.filter(bus=bus, is_booked=True).count()

    def get_features(self, obj):
        return [feature.name for feature in obj.features.all()]

    def create(self, validated_data):
        """
        Create and return a new Bus instance, given the validated data.
        """
        return Bus.objects.create(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['company_name']  

class CreateDriverDetailsSerializer(serializers.ModelSerializer):
    license_image = serializers.ImageField(required=False)
    nrc_image = serializers.ImageField(required=False)
    passport_image = serializers.ImageField(required=False)
    class Meta:
        model = DriverDetails
        fields = '__all__'

class TripScheduleSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=False)
    bus = BusSerializer(required=False)
    driver = CreateDriverDetailsSerializer(required=False)

    class Meta:
        model = TripSchedule
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'price' in representation:
            original_price = Decimal(representation['price'])
            adjusted_price = round(original_price * Decimal('1.03'), 2)  
            representation['price'] = str(adjusted_price)  
        return representation

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        bus_data = validated_data.pop('bus', None)
        driver_data = validated_data.pop('driver', None)
        print('Driver:', driver_data)

        instance = super().update(instance, validated_data)

        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()

        if bus_data:
            bus_serializer = BusSerializer(instance.bus, data=bus_data)
            if bus_serializer.is_valid():
                bus_serializer.save()

        if driver_data:
            driver_serializer = CreateDriverDetailsSerializer(instance.driver, data=driver_data)
            if driver_serializer.is_valid():
                driver_serializer.save()

        return instance


class FeatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feature
        fields = ['name']

    def create(self, validated_data):
        # Get the user who made the request from the serializer context
        user = self.context['request'].user
        # Add the user to the validated data before saving
        validated_data['user'] = user
        return super().create(validated_data)


class BusCreateSerializer(serializers.ModelSerializer):
    features = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(),  # Assuming Feature is the related model
        many=True,
        required=False
    )
    
    seat_picture = serializers.ImageField(required=False)   

    class Meta:
        model = Bus
        fields = '__all__'



class TripSubmissionSerializer(serializers.ModelSerializer):
    passenger_name = serializers.ListField(child=serializers.CharField())
    passenger_phonenumber = serializers.ListField(child=serializers.CharField())
    passenger_email = serializers.ListField(child=serializers.EmailField())
    seat_number = serializers.ListField(child=serializers.IntegerField())
    trip = serializers.PrimaryKeyRelatedField(queryset=TripSchedule.objects.all())
    bus = serializers.PrimaryKeyRelatedField(queryset=Bus.objects.all())
    trip_detail = TripScheduleSerializer(source='trip', read_only=True)
    bus_detail = BusSerializer(source='bus', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'trip',
            'bus',
            'buyer_user_id',
            'passenger_name',
            'passenger_phonenumber',
            'passenger_email',
            'seat_number',
            'active',
            'trip_detail',
            'bus_detail',
        ]


    def create(self, validated_data):
        # Extract the bus instance from validated data
        bus = validated_data.get('bus')
                
        # Extract seat numbers from validated data
        seat_numbers = validated_data.get('seat_number')

        # Mark each seat as booked
        for seat_number in seat_numbers:
            seat, created = Seat.objects.get_or_create(bus=bus, seat_number=seat_number)
            seat.is_booked = True
            seat.save()

        buyer_user_id = validated_data.get('buyer_user_id')

        if not buyer_user_id:
            raise serializers.ValidationError("Invalid User.")

        # Update the active boolean to True
        validated_data['active']=True

        # Call the supercla ss's create method to create the Ticket instance
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['trip_detail'] = TripScheduleSerializer(instance.trip).data
        representation['bus_detail'] = BusSerializer(instance.bus).data
        if instance.qr_code:
            qr_code_url = instance.qr_code.url
            print(f"QR code URL in representation: {qr_code_url}")
            representation['qr_code_url'] = qr_code_url
        return representation

class TicketSerializer(serializers.ModelSerializer):
    
     class Meta:
        model = Ticket
        fields = '__all__'

