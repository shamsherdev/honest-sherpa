from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from superadmin.models import *
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from .serializers import *
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from .email import *
from .jwt import *
from .utils import *
import json
import jwt
from django.contrib.auth.models import auth
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken

# from geopy.geocoders import Nominatim

# Create your views here.


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class RegisterUser(APIView):
    def post(self, request):
        try:
            data = request.data
          
            if data:
                serializer = RegitserSerializer(data=data)
                if not User.objects.filter(email=data["email"].lower()).exists():
                    if serializer.is_valid(raise_exception=False):
                        user = User(email=data["email"].lower(), roll=data["roll"])
                        user.set_password(data["password"])
                        user.save()
                        sendOTP(user)
                        if user.roll in user_type:
                            return Response(
                                {
                                    "status": True,
                                    "message": "Verification code sent on the mail address. Please check",
                                }
                            )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Please select valid user type.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": serializer.errors,
                            }
                        )
                elif User.objects.filter(email=data["email"].lower(), is_verified=True ).exists():
                    user = User.objects.get(email=data['email'])
                    return Response(
                        {
                            "status": False,
                            "is_verified": user.is_verified,
                            "message": "You have already registerd",
                        }
                    )
                else:
                    user = User.objects.get(email=data['email'])
                    if user.roll == data['roll']:
                        sendOTP(user)
                        return Response(
                            {
                                "status": True,
                                "is_verified": user.is_verified,
                                "message": "Your Email address is not verified yet. Please check your email.",
                            }
                        )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": f"This email is associate with {user.roll}. Please select valid user type.",
                            }
                        )
            else:
                return Response(
                    {"status": False,
                    "message": "Please input valid data."}
                )
        except:
            return Response({"status": False,
            "message": "Something went wrong!"})


class ResendOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ResendOTPSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if not user.is_verified:
                            if user.otp_sent_time != None:
                                filter_date = str(user.otp_sent_time)[:19]
                                now_plus_10 = datetime.strptime(
                                    str(filter_date), "%Y-%m-%d %H:%M:%S"
                                ) + timedelta(minutes=10)
                                if datetime.now() >= now_plus_10:
                                    sendOTP(user)
                                    return Response(
                                        {
                                            "status": True,
                                            "message": "Verification code sent on the mail address. Please check",
                                        }
                                    )
                                else:
                                    return Response(
                                        {
                                            "status": False,
                                            "message": f"You can send next otp after 10 mintues. Please try after {str(now_plus_10)[11:]}.",
                                        }
                                    )
                            else:
                                sendOTP(user)
                                return Response(
                                    {
                                        "status": True,
                                        "message": "Verification code sent on the mail address. Please check",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "You have already verify this email address",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "This Email Address not found in our system.",
                            }
                        )
                else:
                    return Response({"status": False, "errors": serializer.errors})
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Please input valid data.",
                    }
                )
        except:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong!",
                }
            )


class VerifyEmialOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = VerifyOTPSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if user.is_verified == True:
                            return Response(
                                {
                                    "status": False,
                                    "message": "You have already verified.",
                                }
                            )
                        if user.OTP == data["otp"]:
                            user.is_verified = True
                            user.OTP = ""
                            user.save()
                            refresh = RefreshToken.for_user(user)
                            user_data = UserViewSerializer(user)
                            return Response(
                                {
                                    "status": True,
                                    "token": str(refresh.access_token),
                                    "payload": user_data.data,
                                    "message": "Email Verification is successfully completed.",
                                }
                            )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "OTP not match. Please try again.",
                                }
                            )
                    else:
                        return Response(
                            {"status": False, "message": "Email not found."}
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "Please Input validate data!",
                        }
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Please Input validate data!",
                    }
                )
        except:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong!",
                }
            )


class LoginUser(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = LoginSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if user.check_password(data["password"]):
                            if user.is_verified == False:
                                sendOTP(user)
                                return Response(
                                    {
                                        "status": True,
                                        "is_verified": user.is_verified,
                                        "message": "Your Email address is not verified yet.",
                                    }
                                )
                            if not user.is_active == True:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Your Account is Inactive. Please contact the Admin.",
                                    }
                                )
                            if not user.check_password(data["password"]):
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Incorrect Password. Please try again!",
                                    }
                                )
                            else:
                                user_view = UserViewSerializer(user)
                                refresh = RefreshToken.for_user(user)
                              
                                auth.authenticate(
                                    email=data["email"].lower(), password=data["password"]
                                )
                                auth.login(request, user)
                                return Response(
                                    {
                                        "status": True,
                                        "token": str(refresh.access_token),
                                        "payload": user_view.data,
                                        "message": "Login Success.",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Incorrect Password. Please try again!",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Email not found.",
                            }
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "Please Input validate data...",
                        }
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Please Input validate data...",
                    }
                )
        except:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong!",
                }
            )


class ChangePasswordSendMail(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ChangePasswordEmailOTPSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if user.is_verified:
                            if user.otp_sent_time != None:
                                filter_date = str(user.otp_sent_time)[:19]
                                now_plus_10 = datetime.strptime(
                                    str(filter_date), "%Y-%m-%d %H:%M:%S"
                                ) + timedelta(minutes=10)
                                if datetime.now() >= now_plus_10:
                                    changePasswordOTP(user)
                                    return Response(
                                        {
                                            "status": True,
                                            "message": "OTP has been sent on email address. Please check Email Address.",
                                        }
                                    )
                                else:
                                    return Response(
                                        {
                                            "status": True,
                                            "message": f"You can send next otp after 10 mintues. Please try after {str(now_plus_10)[11:]}.",
                                        }
                                    )
                            else:
                                changePasswordOTP(user)
                                return Response(
                                    {
                                        "status": True,
                                        "message": "OTP has been sent on email address. Please check Email Address.",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Email address not verified.",
                                }
                            )
                    else:
                        return Response(
                            {"status": False, "message": "Email Not Found."}
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please input valid data."}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data."}
                )
        except:
            return Response({"status": False, "message": "Something went wrong!"})


class ChangePasswordVerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ChangePasswordVerifyEmailOTPSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if user.is_verified == False:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Your Email is not verified yet.",
                                }
                            )
                        if user.OTP != data["otp"]:
                            return Response(
                                {"status": False, "message": "OTP not matched."}
                            )
                        else:
                            # refresh = RefreshToken.for_user(user)
                            return Response(
                                {
                                    "status": True,
                                    # 'token': str(refresh.access_token),
                                    "message": "OTP successfully matched",
                                }
                            )
                    else:
                        return Response(
                            {"status": False, "message": "Email does not Exists."}
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please Input validate data..."}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"status": False, "message": "Something Went Wrong!"})


class ChangePassword(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ChangePasswordSerializer(data=data)
                if serializer.is_valid():
                    if User.objects.filter(email=data["email"].lower()).exists():
                        user = User.objects.get(email=data["email"].lower())
                        if user.is_verified == False or user.is_active == False:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Account not active. Please contact with Admin.",
                                }
                            )
                        if data["new_password"] != data["confirm_password"]:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Password not match. Please try again.",
                                }
                            )
                        else:
                            user.set_password(data["confirm_password"])
                            user.save()
                            return Response(
                                {
                                    "status": True,
                                    "message": "Password Successfully Changed.",
                                }
                            )
                    else:
                        return Response(
                            {"status": False, "message": "Email Address not found."}
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please Input validate data..."}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"status": False, "message": "Something went wrong!"})


class MobileLoginUser(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = MobileLoginSerializer(data=data)
                if serializer.is_valid():
                    if (
                        len(data["mobile_number"]) == 10
                        and data["mobile_number"].isnumeric()
                    ):
                        if User.objects.filter(
                            mobile_number=data["mobile_number"]
                        ).exists():
                            user = User.objects.get(mobile_number=data["mobile_number"])
                            mobile_data = user.mobile_number[6:10]
                            if user.is_active == False or user.is_verified == False:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Your Account is Inactive/Unverified. Please contact the Admin.",
                                    }
                                )
                            else:
                                if user.otp_sent_time == None:
                                    if user.otp_count == str(0):
                                        user.otp_count = int(user.otp_count) + 1
                                        user.save()
                                        return Response(
                                            {
                                                "status": True,
                                                "message": f"OTP send successfully on ***{mobile_data}",
                                            }
                                        )
                                    elif user.otp_count < str(3):
                                        user.otp_count = int(user.otp_count) + 1
                                        if user.otp_count == 3:
                                            user.otp_sent_time = datetime.now()
                                        user.save()
                                        return Response(
                                            {
                                                "status": True,
                                                "message": f"OTP send successfully on ***{mobile_data}",
                                            }
                                        )
                                    else:
                                        return Response(
                                            {
                                                "status": False,
                                                "message": "Your otp send request limit is over for 15 Minutes. Please try again after 15 Minutes.",
                                            }
                                        )
                                else:
                                    filter_date = str(user.otp_sent_time)[:19]
                                    now_plus_15 = datetime.strptime(
                                        str(filter_date), "%Y-%m-%d %H:%M:%S"
                                    ) + timedelta(minutes=15)
                                    if datetime.now() >= now_plus_15:
                                        user.otp_count = 1
                                        user.otp_sent_time = None
                                        user.save()
                                        return Response(
                                            {
                                                "status": True,
                                                "message": f"OTP send successfully on ***{mobile_data}",
                                            }
                                        )
                                    else:
                                        return Response(
                                            {
                                                "status": False,
                                                "message": "Your otp send request limit is over for 15 Minutes. Please try again after 15 Minutes.",
                                            }
                                        )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "This Mobile Number not found in our system.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Mobile Number must be 10 digit or must be numeric only.",
                            }
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "Please Input validate data...",
                        }
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Please Input validate data...",
                    }
                )
        except:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong.",
                }
            )


class VerifMobileyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = MobileLoginOTPVerifySerializer(data=data)
                if serializer.is_valid():
                    if (
                        len(data["mobile_number"]) == 10
                        and data["mobile_number"].isnumeric()
                    ):
                        if User.objects.filter(
                            mobile_number=data["mobile_number"]
                        ).exists():
                            user = User.objects.get(mobile_number=data["mobile_number"])
                            if user.is_verified == False or user.is_active == False:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Your Account or Email not verified.",
                                    }
                                )
                            if data["otp"] != "1234":
                                return Response(
                                    {
                                        "status": False,
                                        "message": "OTP does not match. Please try again.",
                                    }
                                )
                            else:
                                user_view = UserViewSerializer(user)
                                refresh = RefreshToken.for_user(user)
                                return Response(
                                    {
                                        "status": True,
                                        "token": str(refresh.access_token),
                                        "payload": user_view.data,
                                        "message": "Login successfully.",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "This Mobile number not found in our system.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Mobile Number must be 10 digit or must be numeric only.",
                            }
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "Please Input validate data!.",
                        }
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Please Input validate data!.",
                    }
                )
        except:
            return Response(
                {
                    "status": False,
                    "message": "Something Went Wrong.",
                }
            )


class ChangePasswordSendMobileOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = MobileLoginSerializer(data=data)
                if serializer.is_valid():
                    if (
                        len(data["mobile_number"]) == 10
                        and data["mobile_number"].isnumeric()
                    ):
                        if User.objects.filter(
                            mobile_number=data["mobile_number"]
                        ).exists():
                            user = User.objects.get(mobile_number=data["mobile_number"])
                            user_mobile = user.mobile_number[6:10]
                            if user.is_verified == False or user.is_active == False:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Your Account or Email Not verified yet.",
                                    }
                                )
                            else:
                                filter_date = str(user.otp_sent_time)[:19]
                                now_plus_10 = datetime.strptime(
                                    str(filter_date), "%Y-%m-%d %H:%M:%S"
                                ) + timedelta(minutes=10)
                                if datetime.now() >= now_plus_10:
                                    user.otp_sent_time = datetime.now()
                                    user.save()
                                    # sendMobileOTP(user)
                                    return Response(
                                        {
                                            "status": True,
                                            "message": f"OTP has been sent on last 4 ****{user_mobile} digit mobile number.",
                                        }
                                    )
                                else:
                                    return Response(
                                        {
                                            "status": True,
                                            "message": f"You can send next otp after 10 mintues. Please try after {str(now_plus_10)[11:]}.",
                                        }
                                    )
                        else:
                            return Response(
                                {"status": False, "message": "Mobile Number Not Found."}
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Mobile Number must be 10 digit or must be numeric only.",
                            }
                        )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "Please input Valid Mobile Number.",
                        }
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input Valid data!"}
                )
        except:
            return Response(
                {"status": False, "message": "This Mobile Number does not Exists."}
            )


class ChangePasswordMobileOTPVerify(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ChangePasswordMobileOTPSerializer(data=data)
                if serializer.is_valid():
                    if (
                        len(data["mobile_number"]) == 10
                        and data["mobile_number"].isnumeric()
                    ):
                        if User.objects.filter(
                            mobile_number=data["mobile_number"]
                        ).exists():
                            user = User.objects.get(mobile_number=data["mobile_number"])
                            if user.is_verified == False:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Your Email is not verified yet.",
                                    }
                                )
                            if data["otp"] != "12345":
                                return Response(
                                    {"status": False, "message": "OTP not matched."}
                                )
                            else:
                                return Response(
                                    {
                                        "status": True,
                                        "message": "OTP successfully matched",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Mobile Number does not Exists.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Mobile Number must be 10 digit or must be numeric only.",
                            }
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please Input validate data..."}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"status": False, "message": "Something Went Wrong!"})


class ChangePasswordMobile(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ChangePasswordMobileSerializer(data=data)
                if serializer.is_valid():
                    if (
                        len(data["mobile_number"]) == 10
                        and data["mobile_number"].isnumeric()
                    ):
                        if User.objects.filter(
                            mobile_number=data["mobile_number"]
                        ).exists():
                            user = User.objects.get(mobile_number=data["mobile_number"])
                            if user.is_verified == False or user.is_active == False:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Account not active. Please contact with Admin.",
                                    }
                                )
                            if data["new_password"] != data["confirm_password"]:
                                return Response(
                                    {
                                        "status": False,
                                        "message": "Password not match. Please try again.",
                                    }
                                )
                            else:
                                user.set_password(data["confirm_password"])
                                user.save()
                                return Response(
                                    {
                                        "status": True,
                                        "message": "Password Successfully Changed.",
                                    }
                                )
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "Mobile Number does not Exists.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "Mobile Number must be 10 digit or must be numeric only.",
                            }
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please Input validate data..."}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"status": False, "message": "Something went wrong!"})

class PasswordResetAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(token, "secret", algorithms=["HS256"], options=jwt_options)
            user = User.objects.get(id=decode_data["user_id"])
            data = request.data
            if data:
                serializer = PasswordResetSerializer(data=data)
                if serializer.is_valid():
                    if user.check_password(data['old_password']):
                        if check_password(data['new_password']):
                            if user.is_verified == False or user.is_active == False:
                                return Response({
                                    "status": False,
                                    "message": "Account not active. Please contact with Admin.",
                                })
                            if data["new_password"] != data["confirm_password"]:
                                return Response({
                                    "status": False,
                                    "message": "Password not match. Please try again.",
                                })
                            else:
                                if not user.check_password(data["confirm_password"]):
                                    user.set_password(data["confirm_password"])
                                    user.save()
                                    sendAlert(user)
                                    return Response({
                                        "status": True,
                                        "message": "Password Successfully Changed.",
                                    })
                                else:
                                    return Response({
                                        "status": False,
                                        "message": "You can't be set old password as new password.",
                                    })
                        else:
                            return Response({
                                "status": False,
                                "message": "Password must be between 8 to 16 digit and must have contins @1dA.",
                            })
                    else:
                        return Response({
                            "status": False,
                            "message": "Old Password not matched.",
                        })
                else:
                    return Response(
                        {"status": False, "message": "Please input valid data!"}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"status": False, "message": "Something went wrong!"})


class UserProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            if user.roll in user_type:
                serializer = UserViewSerializer(user, context={"request": request})
                return Response(
                    {
                        "status": True,
                        "payload": serializer.data,
                        "message": f"{user.first_name} details are successfully fetched.",
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You have not permission to see profile. Please contact to Admin.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})

    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            data = request.data

            if data:
                serializer = UserProfileSerializer(data=data)
                if serializer.is_valid():
                    if user.roll in user_type:
                        if (
                            User.objects.filter(mobile_number=data["mobile_number"])
                            .exclude(id=user.id)
                            .exists()
                        ):
                            return Response(
                                {
                                    "status": False,
                                    "message": "Mobile Number must be unique.",
                                }
                            )
                        if data["profile_pic"]:
                            user.first_name = data["first_name"]
                            user.last_name = data["last_name"]
                            user.mobile_number = data["mobile_number"]
                            user.profile_pic = data["profile_pic"]
                            user.address = data["address"]
                            user.state = data["state"]
                            user.city = data["city"]
                            user.zip_code = data["zip_code"]
                            user.latitude = data["latitude"]
                            user.longitude = data["longitude"]
                            user.profile_set_up_status = True
                            user.save()
                            user_data = UserViewSerializer(user)
                            return Response(
                                {
                                    "status": True,
                                    "payload": user_data.data,
                                    "message": "Profile updated successfully.",
                                }
                            )
                        else:
                            user.first_name = data["first_name"]
                            user.last_name = data["last_name"]
                            user.mobile_number = data["mobile_number"]
                            user.address = data["address"]
                            user.state = data["state"]
                            user.city = data["city"]
                            user.zip_code = data["zip_code"]
                            user.latitude = data["latitude"]
                            user.longitude = data["longitude"]
                            user.profile_set_up_status = True
                            user.save()
                            user_data = UserViewSerializer(user)
                            return Response(
                                {
                                    "status": True,
                                    "payload": user_data.data,
                                    "message": "Profile updated successfully.",
                                }
                            )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "You have not permission to update profile. Please contact to Admin.",
                            }
                        )
                else:
                    return Response(
                        {"status": False, "message": "Please input valid data!"}
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class StatesAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            json_data = open("country.json")
            data = json.load(json_data)
            if user.roll in user_type:
                return Response(
                    {
                        "status": True,
                        "payload": data.keys(),
                        "total_states": len(data.keys()),
                        "message": "All States are successfully fetched.",
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You have not permission to see states. Please contact to Admin.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class CitiesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            state = self.request.GET["state"]
            json_data = open("country.json")
            data = json.load(json_data)
            if user.roll in user_type:
                if state:
                    return Response(
                        {
                            "status": True,
                            "payload": data[state],
                            "message": f"{state} cities are successfully fetched.",
                        }
                    )
                else:
                    return Response(
                        {"status": False, "message": "Please provide state name."}
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You have not permission to see cities. Please contact to Admin.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class ContactUsAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            if data:
                serializer = ContactUsSerializer(data=data, partial=True)
                if not serializer.is_valid():
                    return Response(
                        {
                            "success": False,
                            "message": serializer.errors,
                        }
                    )
                else:
                    contact_us = Contactus.objects.create(
                        name=data["name"],
                        email=data["email"],
                        question=data["subject"],
                        description=data["message"],
                    )
                    user = contact_us
                    sendTicket(user)
                    return Response(
                        {
                            "status": True,
                            "message": "We have Received your Request. We response soon.",
                        }
                    )
            else:
                return Response(
                    {"status": False, "message": "Please input valid data!"}
                )
        except:
            return Response({"success": False, "message": "Something went wrong"})


class ProductAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):

        # try:
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]

        if token:
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            product_id = self.request.query_params.get("product_id")
            product_name = self.request.query_params.get("product_name")
            product_price = self.request.query_params.get("product_price")
            product_cat = self.request.query_params.get("product_category")
            sort_price = self.request.query_params.get("sort_price")
            pagination = PageNumberPagination()
            pagination.page_size = 10
            pagination.page_size_query_param = "page_size"
            queryset = Q()  # for all queries
            if sort_price:
                if sort_price == "high":
                    sort_price = "-oneday_price"
                if sort_price == "low":
                    sort_price = "oneday_price"
            else:
                sort_price = "-id"
            if product_name:
                queryset &= Q(name__contains=product_name)
            if product_cat:
                queryset &= Q(category__name__contains=product_cat)
            if product_price:
                queryset &= (
                    Q(oneday_price__contains=product_price)
                    | Q(week_price__contains=product_price)
                    | Q(month_price__contains=product_price)
                )
            product = (
                Product.objects.filter(is_active=1)
                .filter(queryset)
                .order_by(f"{sort_price}")
            )
            for_favourite_user_id = decode_data["user_id"]
            product_pagination = pagination.paginate_queryset(product, request)
            if user.roll in user_type:
                if not product_id:
                    serializer = ProductSerializer(
                        product_pagination,
                        many=True,
                        context={
                            "request": request,
                            "user_id": for_favourite_user_id,
                            "product_id": product_id,
                        },
                    )
                    pagination_data = serializer.data
                    pagination_record = pagination.get_paginated_response(
                        pagination_data
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": pagination_record.data,
                            "message": "All Products are successfully fetched.",
                        }
                    )
                else:
                    if Product.objects.filter(id=product_id).exists():
                        product_data = Product.objects.get(id=product_id)
                        serializer = ProductSerializer(
                            product_data,
                            many=False,
                            context={
                                "request": request,
                                "user_id": for_favourite_user_id,
                                "product_id": product_id,
                            },
                        )
                        return Response(
                            {
                                "status": True,
                                "payload": serializer.data,
                                "message": "Product details is successfully fetched.",
                            }
                        )
                    else:
                        return Response(
                            {"status": False, "message": "Product id not found."}
                        )
        else:
            product_id = self.request.query_params.get("product_id")
            product_name = self.request.query_params.get("product_name")
            product_price = self.request.query_params.get("product_price")
            product_cat = self.request.query_params.get("product_category")
            sort_price = self.request.query_params.get("sort_price")
            pagination = PageNumberPagination()
            pagination.page_size = 10
            pagination.page_size_query_param = "page_size"
            queryset = Q()  # for all queries
            if sort_price:
                if sort_price == "high":
                    sort_price = "-oneday_price"
                if sort_price == "low":
                    sort_price = "oneday_price"
            else:
                sort_price = "-id"
            if product_name:
                queryset &= Q(name__contains=product_name)
            if product_cat:
                queryset &= Q(category__name__contains=product_cat)
            if product_price:
                queryset &= (
                    Q(oneday_price__contains=product_price)
                    | Q(week_price__contains=product_price)
                    | Q(month_price__contains=product_price)
                )
            product = (
                Product.objects.filter(is_active=1)
                .filter(queryset)
                .order_by(f"{sort_price}")
            )
            product_pagination = pagination.paginate_queryset(product, request)
            if not product_id:
                serializer = ProductSerializer(
                    product_pagination, many=True, context={"request": request}
                )
                pagination_data = serializer.data
                pagination_record = pagination.get_paginated_response(pagination_data)
                return Response(
                    {
                        "status": True,
                        "payload": pagination_record.data,
                        "message": "All Products are successfully fetched.",
                    }
                )
            else:
                if Product.objects.filter(id=product_id).exists():
                    product_data = Product.objects.get(id=product_id)
                    serializer = ProductSerializer(
                        product_data,
                        many=False,
                        context={
                            "request": request,
                        },
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": serializer.data,
                            "message": "Product details is successfully fetched.",
                        }
                    )

            return Response({"success": False, "message": "Something Went Wrong"})

    # except:
    #     return Response({"success": False, "message": "Something Went Wrong"})


class ProductCategoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            if token:
                decode_data = jwt.decode(
                    token, "secret", algorithms=["HS256"], options=jwt_options
                )
                user = User.objects.get(id=decode_data["user_id"])
                product_category = ProductCategory.objects.filter(is_active=1).order_by(
                    "id"
                )
                if user.roll in user_type:
                    serializer = ProductCategorySerializer(
                        product_category, many=True, context={"request": request}
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": serializer.data,
                            "message": "All Products Category are successfully fetched.",
                        }
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "You have not permission to see Products Category. Please contact to Admin.",
                        }
                    )
            else:

                product_category = ProductCategory.objects.filter(is_active=1).order_by(
                    "id"
                )
                serializer = ProductCategorySerializer(
                    product_category, many=True, context={"request": request}
                )
                return Response(
                    {
                        "status": True,
                        "payload": serializer.data,
                        "message": "Home data fetched.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class ProductSubCategoryAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            if token:
                decode_data = jwt.decode(token, "secret", algorithms=["HS256"], options=jwt_options)
                user = User.objects.get(id=decode_data["user_id"])
                category_id = self.request.query_params.get("category_id")
                product_subcategory = ProductSubCategory.objects.filter(category_id=category_id).order_by("-id")
                if user.roll in user_type:
                    serializer = ProductSubCategorySerializer(
                        product_subcategory, many=True, context={"request": request}
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": serializer.data,
                            "message": "All Products Category are successfully fetched.",
                        }
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "You have not permission to see Products Category. Please contact to Admin.",
                        }
                    )
            else:
                category_id = self.request.query_params.get("category_id")
                product_subcategory = ProductSubCategory.objects.filter(
                    category_id=category_id
                ).order_by("-id")
                serializer = ProductSubCategorySerializer(
                    product_subcategory, many=True, context={"request": request}
                )
                return Response(
                    {
                        "status": True,
                        "payload": serializer.data,
                        "message": "All Products Category are successfully fetched.",
                    }
                )
                # return Response(
                #     {
                #         "status": False,
                #         "message": "Subcategory Not Found",
                #     }
                # )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class AppSliderAPI(APIView):
    def get(self, request):
        try:
            slider = AppSlider.objects.all().order_by("-id")
            serializer = AllSliderSerializer(
                slider, many=True, context={"request": request}
            )
            return Response(
                {
                    "status": True,
                    "payload": serializer.data,
                    "message": "Sliders are successfully fetched.",
                }
            )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class HomeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            user = User.objects.get(id=decode_data["user_id"])
            product_category = Product.objects.filter(is_active=1).order_by("-id")
            if user.roll in user_type:
                serializer = HomeAppSerializer(
                    product_category, many=True, context={"request": request}
                )
                return Response(
                    {
                        "status": True,
                        "payload": serializer.data,
                        "message": "All Products Category are successfully fetched.",
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You have not permission to see Products Category. Please contact to Admin.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class ProductDataAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            if token:
                decode_data = jwt.decode(
                    token, "secret", algorithms=["HS256"], options=jwt_options
                )
                user = User.objects.get(id=decode_data["user_id"])
                sub_category = self.request.query_params.get("sub_category")
                pagination = PageNumberPagination()
                pagination.page_size = 10
                pagination.page_size_query_param = "page_size"
                product = Product.objects.filter(
                    is_active=1, subcategory_id=sub_category
                ).order_by("-id")
                product_pagination = pagination.paginate_queryset(product, request)
                if user.roll in user_type:
                    serializer = ProductSerializer(
                        product_pagination, many=True, context={"request": request}
                    )
                    pagination_data = serializer.data
                    pagination_record = pagination.get_paginated_response(
                        pagination_data
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": pagination_record.data,
                            "message": "All Products are successfully fetched.",
                        }
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "You have not permission to see Product. Please contact to Admin.",
                        }
                    )
            else:
                sub_category = self.request.query_params.get("sub_category")
                pagination = PageNumberPagination()
                pagination.page_size = 10
                pagination.page_size_query_param = "page_size"
                product = Product.objects.filter(
                    is_active=1, subcategory_id=sub_category
                ).order_by("-id")
                product_pagination = pagination.paginate_queryset(product, request)
                serializer = ProductSerializer(
                    product_pagination, many=True, context={"request": request}
                )
                pagination_data = serializer.data
                pagination_record = pagination.get_paginated_response(pagination_data)
                return Response(
                    {
                        "status": True,
                        "payload": pagination_record.data,
                        "message": "All Products are successfully fetched.",
                    }
                )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class AppHomeAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            latitude = self.request.query_params.get("latitude")
            longitude = self.request.query_params.get("longitude")
            if token:
                decode_data = jwt.decode(
                    token, "secret", algorithms=["HS256"], options=jwt_options
                )
                user = User.objects.get(id=decode_data["user_id"])
                app_banner = AppBanner.objects.all().order_by("-id")
                if user.roll in user_type:
                    serializer = AllBannerSerializer(
                        app_banner,
                        many=True,
                        context={
                            "request": request,
                            "latitude": latitude,
                            "longitude": longitude,
                        },
                    )
                    return Response(
                        {
                            "status": True,
                            "payload": serializer.data,
                            "latitude": latitude,
                            "longitude": longitude,
                            "message": "Home data fetched.",
                        }
                    )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "You have not permission to see Home Screen. Please contact to Admin.",
                        }
                    )
            else:
                app_banner = AppBanner.objects.all().order_by("-id")
                serializer = AllBannerSerializer(
                    app_banner,
                    many=True,
                    context={
                        "request": request,
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )
                return Response(
                    {
                        "status": True,
                        "payload": serializer.data,
                        "latitude": latitude,
                        "longitude": longitude,
                        "message": "Home data fetched.",
                    }
                )

        except:
            return Response({"success": False, "message": "Something Went Wrong"})


class ProductFavouriteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
            decode_data = jwt.decode(
                token, "secret", algorithms=["HS256"], options=jwt_options
            )
            data = ProductFavourite.objects.filter(user_id=decode_data["user_id"])
            serializer = ProductFavouriteSerializer(data, many=True)
            return Response(
                {
                    "status": True,
                    "payload": serializer.data,
                    "message": "All Favourite Products are successfully fetched.",
                }
            )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})

    def post(self, request):
        data = request.data
        token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")[1]
        decode_data = jwt.decode(
            token, "secret", algorithms=["HS256"], options=jwt_options
        )
        serializer = ProductFavouriteSerializer(data=data)
        user = User.objects.get(id=decode_data["user_id"])
        if serializer.is_valid(raise_exception=False):
            if Product.objects.filter(id=data["product_id"]).exists():
                if data["favourite"] == "1":
                    product_data = ProductFavourite.objects.create(
                        user_id=decode_data["user_id"],
                        product_id=data["product_id"],
                        is_favourite=True,
                    )
                    serializer = ProductFavouriteSerializer(product_data)
                    return Response(
                        {
                            "status": True,
                            "payload": serializer.data,
                            "message": "Product favourite.",
                        }
                    )
                else:
                    product_fav = ProductFavourite.objects.get(
                        product_id=data["product_id"], user_id=decode_data["user_id"]
                    )
                    product_fav.delete()
                    return Response(
                        {
                            "status": True,
                            "message": "Product unfavourite.",
                        }
                    )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Product not found.",
                    }
                )
        else:
            return Response(
                {
                    "status": False,
                    "message": "Please input valid data.",
                }
            )


class AppBannerAPI(APIView):
    def get(self, request):
        try:
            data = AppBanner.objects.all()
            serializer = AppBannerSerializer(data, many=True)
            return Response(
                {
                    "status": True,
                    "payload": serializer.data,
                    "message": "All Banners are successfully fetched.",
                }
            )
        except:
            return Response({"success": False, "message": "Something Went Wrong"})