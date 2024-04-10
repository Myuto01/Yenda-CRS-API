# utils.py
from .models import User
import random
import string

def generate_otp_for_user_from_session(request):
    # Retrieve user data from the session
    user_data = request.session.get('temp_user_data')
    if not user_data:
        raise ValueError("User data not found in session")

    # Remove the 'password2' field from user data if present
    user_data.pop('password2', None)

    # Create a new user object in memory without saving it to the database
    user = User(**user_data)

    otp_value = ''.join(random.choices(string.digits, k=5))

    # Store OTP value in the session
    request.session['otp'] = otp_value
    request.session.save()

    return otp_value

def generate_otp_for_new_number(request):
    # Retrieve user data from the session
    phone_number = request.session.get('temp_phone_number')

    if not phone_number:
        raise ValueError("Phone number not found in session")

    otp_value = ''.join(random.choices(string.digits, k=5))

    # Store OTP value in the session
    request.session['otp'] = otp_value
    request.session.save()

    return otp_value

