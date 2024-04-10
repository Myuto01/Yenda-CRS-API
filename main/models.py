from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField 
import datetime
import random

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





