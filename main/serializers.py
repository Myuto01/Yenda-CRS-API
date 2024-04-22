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

    class Meta:
        model = Bus
        fields = [ 
            'id',
            'bus_type',
            'total_seats',
            'number_plate',
            'features', 
            'status', 
            'seat_picture'
        ]

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



class TripScheduleSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    bus = BusSerializer()

    class Meta:
        model = TripSchedule
        fields = [
            'user',
            'bus', 
            'origin', 
            'destination',
            'departure_date',
            'departure_time',
            'price'
        ]
"""
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        # Convert departure_date string to datetime object
        if instance.departure_date:
            if isinstance(instance.departure_date, str):
                representation['departure_date'] = datetime.datetime.strptime(instance.departure_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            else:
                representation['departure_date'] = instance.departure_date.strftime('%Y-%m-%d')
        # Convert departure_time string to datetime object
        if instance.departure_time:
            if isinstance(instance.departure_time, str):
                representation['departure_time'] = datetime.datetime.strptime(instance.departure_time, '%H:%M:%S').strftime('%H:%M:%S')
            else:
                representation['departure_time'] = instance.departure_time.strftime('%H:%M:%S')
        
        return representation
"""
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
        fields = ['bus_type', 'total_seats', 'number_plate', 'status', 'features', 'seat_picture']


class CreateDriverDetailsSerializer(serializers.ModelSerializer):
    license_image = serializers.ImageField(required=False)
    nrc_image = serializers.ImageField(required=False)
    passport_image = serializers.ImageField(required=False)
    class Meta:
        model = DriverDetails
        fields = '__all__'

class TripSubmissionSerializer(serializers.ModelSerializer):
    passenger_name = serializers.ListField(child=serializers.CharField())
    passenger_phonenumber = serializers.ListField(child=serializers.CharField())
    passenger_email = serializers.ListField(child=serializers.EmailField())
    seat_number = serializers.ListField(child=serializers.IntegerField())

    # Add custom fields for trip and bus IDs
    trip_id = serializers.PrimaryKeyRelatedField(queryset=TripSchedule.objects.all(), source='trip', write_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(queryset=Bus.objects.all(), source='bus', write_only=True)

    class Meta:
        model = Ticket
        fields = [
            'trip_id',
            'bus_id',
            'passenger_name',
            'passenger_phonenumber',
            'passenger_email',
            'seat_number',
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

        # Call the superclass's create method to create the Ticket instance
        return super().create(validated_data)