from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField 
import datetime
from datetime import time
import random
import qrcode
from io import BytesIO
from django.core.files import File

def profile_pics_upload_path(instance, filename):
    # Upload to "citizen_id/username/front" or "citizen_id/username/back"
    return f'profile_pics/{instance.phone_number}/{filename}'

class User(AbstractBaseUser, PermissionsMixin):
    company_name = models.CharField(max_length=30, null=False, unique=True, default="")
    contact_person = models.CharField(max_length=30, null=False, default="")
    email = models.EmailField(max_length=30, unique=True, null=False, default="")
    phone_number = PhoneNumberField(unique=True, blank=True)  
    business_licence_number = models.CharField(max_length=30, null=False, unique=True, default="")
    profile_pic = models.ImageField(default='default1.jpg', null=True, blank=True, upload_to=profile_pics_upload_path)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  

    REQUIRED_FIELDS = ["company_name", "contact_person", 'phone_number', 'business_licence_number' ]

    objects = UserManager()

    def __str__(self):
        return str(self.company_name)

    
    def get_phone_number(self):
        return str(self.phone_number)

    @property
    def get_full_name(self):
        return f"{self.company_name}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class Bus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=10)
    bus_type = models.CharField(max_length=30, blank=True, null=True, default="")
    total_seats = models.IntegerField(blank=True, null=True, default=0)
    number_plate = models.CharField(max_length=10, blank=True, null=True, default="")
    features = models.ManyToManyField('Feature', blank=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    seat_picture = models.ImageField(upload_to='media/buses/', null=True, blank=True)

    def __str__(self):
        return f"User: {self.user}, Bus: {self.bus_type}, Number Plate: {self.number_plate}"

class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Seat {self.seat_number} of Bus {self.bus.number_plate}"





class Feature(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=10)

    features = models.ManyToManyField('self', blank=True)

    name = models.CharField(max_length=20, default="")

    def __str__(self):
       return self.name

    



class TripSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=10)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)  
    origin = models.CharField(max_length=30, blank=True, default="")
    destination = models.CharField(max_length=30, blank=True, default="")
    departure_date =  models.DateTimeField(default=datetime.datetime.now)
    departure_time =  models.TimeField(default=time(12, 0, 0))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"User: {self.user}, Bus: {self.bus}, Origin: {self.origin}, Destination: {self.destination}, Departure Date: {self.departure_date}, Departure Time: {self.departure_time}"

class DriverDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=10)
    driver_name = models.CharField(max_length=30, blank=True, null=True, default="")
    license_number = models.CharField(max_length=30, blank=True, null=True, default="")
    nrc_number = models.CharField(max_length=30, blank=True, null=True, default="")
    phone_number = models.CharField(max_length=10, blank=True, null=True, default="")
    passport_number = models.CharField(max_length=30, blank=True, null=True, default="")
    license_image = models.ImageField(upload_to='media/license_image/', null=True, blank=True)
    nrc_image = models.ImageField(upload_to='media/nrc_image/', null=True, blank=True)
    passport_image = models.ImageField(upload_to='media/passport_image/', null=True, blank=True)


class Ticket(models.Model):
    trip = models.ForeignKey(TripSchedule, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, default="")
    passenger_name = models.CharField(max_length=255, default="", null=True)
    passenger_phonenumber = models.CharField(max_length=255)
    passenger_email = models.CharField(max_length=255, default="")
    seat_number = models.CharField(max_length=255, default="")
    confirmed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    buyer_user_id = models.IntegerField(default=0)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        # Construct QR code data
        qr_data = f"Trip: {self.trip},Trip_id: {self.trip.id}, Bus: {self.bus},Bus_id: {self.bus.id}, Number Plate: {self.bus.number_plate}, Origin: {self.trip.origin}, Destination: {self.trip.destination}, Departure Date: {self.trip.departure_date}, Departure Time: {self.trip.departure_time}, Passenger Name: {self.passenger_name}, Seat Number: {self.seat_number}"
        
        # Generate QR code image
        qr = qrcode.make(qr_data)

        # Create a BytesIO object to hold the image data
        img_io = BytesIO()

        # Save the image to the BytesIO object in JPEG format
        qr.save(img_io, 'JPEG')

        # Set the position to the beginning of the stream
        img_io.seek(0)

        # Set the QR code image field with the BytesIO object
        self.qr_code.save(f'qr_code_{self.pk}.jpg', File(img_io), save=False)

        super().save(*args, **kwargs)

