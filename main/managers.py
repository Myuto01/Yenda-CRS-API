from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

    def create_user(self, company_name, contact_person, email, phone_number, business_licence_number, password=None, **extra_fields):
        # Check for required fields
        if not company_name:
            raise ValidationError(_("Company name is required"))
        if not contact_person:
            raise ValidationError(_("Contact person is required"))
        if not email:
            raise ValidationError(_("Email is required"))
        if not phone_number:
            raise ValidationError(_("The phone number must be set"))
        if not business_licence_number:
            raise ValidationError(_("Business Licence number is required"))

        # Create user instance
        user = self.model(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            phone_number=phone_number,
            business_licence_number=business_licence_number,
            **extra_fields
        )

        # Set and hash the password
        if password is not None:
            user.set_password(password)
        
        # Save user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, company_name, contact_person, email, phone_number, business_licence_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True) 
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("is_staff must be True for admin user"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("is_superuser must be True for admin user"))

        user = self.create_user(company_name, contact_person, email, phone_number, business_licence_number, password=password, **extra_fields)
        return user

