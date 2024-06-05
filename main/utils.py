# utils.py
from .models import User
import random
import string
from .pay import PayClass

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

def mtn_mobile_money_pay(phone_number, total_price, reference):

    amount = total_price
    currency = 'EUR' 
    txt_ref = reference
    payermessage = "Ticket payment"

    # Initialize the payment request
    callPay = PayClass.momopay(amount, currency, txt_ref, phone_number, payermessage)


    # Check and print the response
    if "response" in callPay and "ref" in callPay:
    

        # Verify the payment using the reference
        verify = PayClass.verifymomo(callPay["ref"])

        if "code" in verify and verify["code"] == "RESOURCE_NOT_FOUND":
            print("Error: Resource not found - Full Response:", verify)

        # Returning the response and verification
        return {
            "payment_response": callPay["response"],
            "payment_reference": callPay["ref"],
            "verification_response": verify
        }
    else:
        print("Error in payment response:", callPay)

def mtn_mobile_money_disbursment(operator_phone_number, operator_amount, reference):
    amount = operator_amount
    currency = 'EUR' 
    txt_ref = reference
    payermessage = "Ticket payment"

    # Initialize the payment request
    withdrawmoney = PayClass.withdrawmtnmomo(amount, currency, txt_ref, operator_phone_number, payermessage)

    # Check and print the response
    if "response" in withdrawmoney and "ref" in withdrawmoney:

        # Verify the payment using the reference
        CheckWithdrawStatus = PayClass.checkwithdrawstatus(withdrawmoney["ref"])


        if "code" in CheckWithdrawStatus and CheckWithdrawStatus["code"] == "RESOURCE_NOT_FOUND":
            print("Error: Resource not found - Full Response:", CheckWithdrawStatus)

        # Returning the response and verification
        return {
            "payment_response": withdrawmoney["response"],
            "payment_reference": withdrawmoney["ref"],
            "verification_response": CheckWithdrawStatus
        }
    else:
        print("Error in payment response:", withdrawmoney)


