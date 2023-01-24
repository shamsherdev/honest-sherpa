from django.urls import path
from . import views

from .views import *

urlpatterns = [
    path("register/", RegisterUser.as_view()),
    path("otp-verify/", VerifyEmialOTP.as_view()),
    path("otp-resend/", ResendOTP.as_view()),
    path("login/", LoginUser.as_view()),
    path("passwordReset/", PasswordResetAPI.as_view()),
    path("changePassword/step1/", ChangePasswordSendMail.as_view()),
    path("changePassword/step2/", ChangePasswordVerifyOTP.as_view()),
    path("changePassword/step3/", ChangePassword.as_view()),
    path("mobileLogin/", MobileLoginUser.as_view()),
    path("mobileLogin/otp-verify/", VerifMobileyOTP.as_view()),
    path("changePasswordMobile/step1/", ChangePasswordSendMobileOTP.as_view()),
    path("changePasswordMobile/step2/", ChangePasswordMobileOTPVerify.as_view()),
    path("changePasswordMobile/step3/", ChangePasswordMobile.as_view()),
    path("profile-view/", UserProfile.as_view()),
    path("states-lists/", StatesAPI.as_view()),
    path("cities-lists/", CitiesAPI.as_view()),
    path("products-lists/", ProductAPI.as_view()),
    path("productsCategory-lists/", ProductCategoryAPI.as_view()),
    path("contact-us/", ContactUsAPI.as_view()),
    path("app-slider/", AppSliderAPI.as_view()),
    path("sub-category-lists/", ProductSubCategoryAPI.as_view()),
    path("products/", ProductDataAPI.as_view()),
    path("homeAPI/", AppHomeAPI.as_view()),
    path("productfavouriteAPI/", ProductFavouriteAPI.as_view()),
    path("appBanner/", AppBannerAPI.as_view()),
]
