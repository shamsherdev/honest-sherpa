from dis import dis
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, request
from django.shortcuts import render, redirect
from numpy import greater
from superadmin.models import *
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.hashers import (
    MD5PasswordHasher,
    make_password,
    
    check_password,
)
from superadmin.helper import *
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date
from honest_app.helpers import *
from django.contrib.sessions.models import Session
from api.utils import *
import pgeocode
from django.contrib.auth.decorators import login_required
import geocoder
from django.conf import settings
from django.core.mail import send_mail, EmailMessage

import threading
from django.db.models import Avg
from django.core.paginator import Paginator
from datetime import date
from django.db.models import Sum





User = get_user_model()


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(
            self.subject,
            self.html_content,
            settings.EMAIL_HOST_USER,
            self.recipient_list,
        )
        msg.send()

@csrf_exempt
def location_pincode(request):
    if request.method == "POST":
        pincode = request.POST.get("pincode")
        print(pincode,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
       
        if pincode:
            request.session["pin_code"] = pincode
            request.session.modified = True
            return JsonResponse({"status": "success", "sucess": True})
        print(request.session.has_key("pin_code"), "=-===-=")
        if request.session.has_key("pin_code"):
            del request.session["pin_code"]
            request.session.modified = True
        return JsonResponse({"status": "failure", "sucess": False})

    return JsonResponse({"status": "failure", "sucess": False})


   

# @login_required(login_url='/login/')
def home(request):
    request.session["id"] = []
    blog = Blog.objects.all()
    globalseeting = GlobalSetting.objects.get(id=1)
    add_cart_products_count = AddToCart.objects.filter(user_id=request.user.id).count()

    if request.session.get("pin_code") is not None:
        pincode = request.session.get("pin_code")
        product = Product.objects.filter(is_active=True)[:8]
        feature_product = Product.objects.filter(is_active=True, is_feature=True)[:8]
        category = ProductCategory.objects.filter(is_active=True)
        like_product = []
        fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
        add_to_cart_product_list = []

        for i in fav_product:
            like_product.append(i.product_id)
        banner = pages.objects.filter(
            Q(slug="Home-banner-page1")
            | Q(slug="Home-banner-page2")
            | Q(slug="Home-banner-page3")
        )
        banner_about_us = pages.objects.get(slug="Home-About-Us")
        banner_how_it_work = pages.objects.get(slug="Home-how-it-works")
        option_list = []
        feature_product_option_list = []
        for i in product:
            option = ProductOptions.objects.filter(product_id=i.id)
            for x in option:
                option_list.append(x)
            add_to_cart_product = AddToCart.objects.filter(
                user_id=request.user.id, product_id=i.id
            )
           
            if add_to_cart_product:
                add_to_cart_product_list.append(i.id)

        for j in feature_product:
            feature_product_option = ProductOptions.objects.filter(product_id=j.id)
            for x in feature_product_option:
                feature_product_option_list.append(x)
        # product_price = FranchisePinCodesPrice.objects.filter(pin_code=pincode)
        # pin_code = FranchisePinCodes.objects.all()
        # pin_code_id=pin_code[0].id
        # pin_code_price = FranchisePinCodes.objects.get(pincode)
       
        if request.user.is_authenticated:
            
            product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pincode, user_type=request.user.roll)
          
        else:
            product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pincode, user_type="vacationer" )
            print(product_price,'ewewwwwwwwwwwwwwwwwwwwwwwww')
          
        # is_user_commented = product_price.filter(user_tyoe="vacationer").exists()
        # request.session.clear()

        return render(
            request,
            "web/home.html",
            {
                "product": product,
                "option": option_list,
                "feature_product": feature_product,
                "feature_product_option": feature_product_option_list,
                "category": category,
                "banner": banner,
                "banner_about_us": banner_about_us,
                "banner_how_it_work": banner_how_it_work,
                "fav_product": like_product,
                "add_cart": add_to_cart_product_list,
                "blog": blog,
                "product_price": product_price,
                # "pin_code_price":pin_code_price,
                "globalseeting": globalseeting,
                "add_cart_products_count":add_cart_products_count,
            },
        )

    else:
        product = Product.objects.filter(is_active=True)[:8]
        feature_product = Product.objects.filter(is_active=True, is_feature=True)[:8]
        category = ProductCategory.objects.filter(is_active=True)
        like_product = []
        fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
        add_to_cart_product_list = []

        for i in fav_product:
            like_product.append(i.product_id)
        banner = pages.objects.filter(
            Q(slug="Home-banner-page1")
            | Q(slug="Home-banner-page2")
            | Q(slug="Home-banner-page3")
        )
        banner_about_us = pages.objects.get(slug="Home-About-Us")
        banner_how_it_work = pages.objects.get(slug="Home-how-it-works")
        option_list = []
        feature_product_option_list = []
        for i in product:
            option = ProductOptions.objects.filter(product_id=i.id)
            for x in option:
                option_list.append(x)
            add_to_cart_product = AddToCart.objects.filter(
                user_id=request.user.id, product_id=i.id
            )
         

            if add_to_cart_product:
                add_to_cart_product_list.append(i.id)

        for j in feature_product:
            feature_product_option = ProductOptions.objects.filter(product_id=j.id)
            for x in feature_product_option:
                feature_product_option_list.append(x)
        # pin_code = FranchisePinCodes.objects.all()
        # pin_code_id=pin_code[0].id
        # pin_code_price = FranchisePinCodes.objects.get(id=pin_code_id)
        # if request.user.is_authenticated:
            
        #     product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code_price.pin_code, user_type=request.user.roll)
          
        # else:
        #     product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code_price.pin_code, )
          
        
        return render(
            request,
            "web/home.html",
            {
                # "product_price": product_price,
                "product": product,
                "option": option_list,
                "feature_product": feature_product,
                "feature_product_option": feature_product_option_list,
                "category": category,
                "banner": banner,
                "banner_about_us": banner_about_us,
                "banner_how_it_work": banner_how_it_work,
                "fav_product": like_product,
                "add_cart": add_to_cart_product_list,
                "blog": blog,
                "globalseeting": globalseeting,
                "add_cart_products_count":add_cart_products_count,
            },
        )


def sign_up(request):
    try:
        data = request.POST
        if request.method == "POST":
            email = request.POST.get("email")

            password = request.POST.get("password")

            confirm_password = request.POST.get("confirm_password")

            user_type = request.POST.get("user_type")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists !!!!")
                return render(request, "web/auth/sign-up.html", {"data": data})
            elif password != confirm_password:
                messages.error(request, "Password does not match !!!!")
                return render(request, "web/auth/sign-up.html", {"data": data})
            else:

                # send_mail(subject, message, email_from, recipient_list)
                if user_type == "propertymanager":
                    pro_user_type = request.POST.get("propertyManagerType")
                    if pro_user_type == "Company":
                        user = User.objects.create(
                            email=email,
                            password=make_password(password),
                            roll=user_type,
                            is_active="0",
                            property_manager_type="Company",
                        )
                        user.save()

                        return redirect("/select_property_company/" + str(user.slug))
                    else:
                        otp = generateOTP()
                        subject = "Welcome to Honest Sherpa world"
                        message = f"Hi {email}, thank you for registering in as a {user_type} on Honest Sherpa.Your one time password is {otp}"
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = email
                        EmailThread(subject, message, [recipient_list]).start()
                        user = User.objects.create(
                            email=email,
                            password=make_password(password),
                            roll=user_type,
                            OTP=otp,
                            is_active="0",
                            property_manager_type="Individual",
                        )
                        user.save()
                        messages.success(request, "Please verify your otp !!!!")
                        return redirect("/verify/sign-up/otp/" + str(user.slug))
                else:
                    otp = generateOTP()
                    subject = "Welcome to Honest Sherpa world"
                    message = f"Hi {email}, thank you for registering in as a {user_type} on Honest Sherpa.Your one time password is {otp}"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = email
                    EmailThread(subject, message, [recipient_list]).start()
                    user = User.objects.create(
                        email=email,
                        password=make_password(password),
                        roll=user_type,
                        OTP=otp,
                        is_active=True,
                    )
                    user.save()
                    messages.success(request, "Please verify your otp !!!!")
                    return redirect("/verify/sign-up/otp/" + str(user.slug))

        return render(request, "web/auth/sign-up.html")
    except:
        messages.error(request, "something went wrong")

        return render(request, "web/auth/sign-up.html")


def select_property_company(request, slug):
    try:

        if request.method == "POST":
            user = User.objects.get(slug=slug)

            compnayName = request.POST.get("propertmanagercompany")
            company_name = request.POST.get("company_name")
            company_email = request.POST.get("company_email")
            company_contact = request.POST.get("company_contact")
            company_address = request.POST.get("company_address")

            company_zip = request.POST.get("company_zip")

            if PropertyManagerMember.objects.filter(
                companyzip_code=company_zip
            ).exists():
                propertmanager = PropertyManagerMember.objects.filter(
                    is_verified=True
                ).exclude(slug=slug)

                messages.error(request, "Zip Code already Exist")
                return render(
                    request,
                    "web/auth/select-property-company.html",
                    {"propertmanager": propertmanager, "user": user},
                )
            otp = generateOTP()
            subject = "Welcome to Honest Sherpa world"
            message = f"Hi {user.email}, thank you for registering in as a {user_type} on Honest Sherpa.Your one time password is {otp}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = user.email
            EmailThread(subject, message, [recipient_list]).start()

            if compnayName == "others":

                data = PropertyManagerMember.objects.create(
                    user_id=user.id,
                    companyname=company_name,
                    companyemail=company_email,
                    companycontact=company_contact,
                    companyaddress=company_address,
                    companyzip_code=company_zip,
                )
                data.save()
                user.company_status = True

                user.OTP = otp
                user.save()
                messages.success(request, "Please verify your otp !!!!")
                return redirect("/verify/sign-up/otp/" + str(slug))

            else:
                data = SelectProertyManagerCompany.objects.create(
                    user_id=user.id, company_id=compnayName
                )
                user.company_status = True

                user.OTP = otp

                user.save()
                messages.success(request, "Please verify your otp !!!!")
                return redirect("/verify/sign-up/otp/" + str(slug))
        user = User.objects.get(slug=slug)

        propertmanager = PropertyManagerMember.objects.filter(is_verified=True).exclude(
            slug=slug
        )

        return render(
            request,
            "web/auth/select-property-company.html",
            {"propertmanager": propertmanager, "user": user},
        )
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/select_property_company/" + str(slug))


def verify_signup_otp(request, slug):
    try:
        user = User.objects.get(slug=slug)
        property = PropertyManagerMember.objects.filter(user_id=user)

        if request.method == "POST":
            otp1 = request.POST.get("otp1")
            otp2 = request.POST.get("otp2")
            otp3 = request.POST.get("otp3")
            otp4 = request.POST.get("otp4")
            Otp = str(otp1) + str(otp2) + str(otp3) + str(otp4)
            if user.OTP == Otp:
                if user.roll == "propertymanager":
                    # auth.login(request, user)
                    user.OTP = ""
                    user.is_verified = True

                    user.save()
                    for pro in property:
                        pro.is_verified = True
                        pro.save()
                    messages.success(request, "otp match successfully")
                    return redirect("/profile/setup/" + str(slug))
                else:
                    user.OTP = ""
                    user.is_verified = True
                    user.is_active = True
                    user.save()
                    for pro in property:
                        pro.is_verified = True
                        pro.save()
                    messages.success(request, "otp match successfully")
                    return redirect("/profile/setup/" + str(slug))
            else:
                messages.error(request, "otp does not matched")
                return redirect("/verify/sign-up/otp/" + str(slug))
        return render(request, "web/auth/verification.html", {"slug": slug})
    except:
        messages.error(request, "Something went wrong")
        return render(request, "web/auth/verification.html", {"slug": slug})


def sign_up_resend_otp(request, slug):
    try:
        user = User.objects.get(slug=slug)
        # em = email_templates.objects.get(id=3)
        if user.otp_sent_time != None:
            filter_date = str(user.otp_sent_time)[:19]
            now_plus_10 = datetime.datetime.strptime(
                str(filter_date), "%Y-%m-%d %H:%M:%S"
            ) + timedelta(minutes=5)
            if datetime.datetime.now() >= now_plus_10:
                user.otp_count = "0"
                user.otp_count = int(user.otp_count) + 1
                otp = generateOTP()
                user.OTP = otp
                user.otp_sent_time = datetime.datetime.now()
                user.save()
                subject = "Welcome to Honest Sherpa world"
                message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = user.email
                EmailThread(subject, message, [recipient_list]).start()

                # send_mail(subject, message, email_from, recipient_list)
                # sendsms(to, text)
                messages.success(request, "Otp sent successfully !!!")
                return redirect("/verify/sign-up/otp/" + str(slug))
            else:
                if user.otp_count >= str(3):
                    messages.error(
                        request,
                        f"You can send next otp after 5 mintues. Please try after {str(now_plus_10)[11:]}",
                    )
                    return redirect("/verify/sign-up/otp/" + str(slug))
                else:
                    user.otp_count = int(user.otp_count) + 1
                    otp = generateOTP()
                    user.OTP = otp
                    user.otp_sent_time = datetime.datetime.now()
                    user.save()
                    subject = "Welcome to Honest Sherpa world"
                    message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = user.email
                    EmailThread(subject, message, [recipient_list]).start()

                    # send_mail(subject, message, email_from, recipient_list)
                    # sendsms(to, text)
                    messages.success(request, "Otp sent successfully !!!")
                    return redirect("/verify/sign-up/otp/" + str(slug))
        else:
            otp = generateOTP()
            user.OTP = otp
            user.otp_sent_time = datetime.datetime.now()
            user.save()
            subject = "Welcome to Honest Sherpa world"
            message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = user.email
            EmailThread(subject, message, [recipient_list]).start()

            # send_mail(subject, message, email_from, recipient_list)
            return redirect("/verify/sign-up/otp/" + str(slug))
    except:
        messages.error(request, "Something went wrong")
        return redirect("/verify/sign-up/otp/" + str(slug))


def profile_setup(request, slug):
    try:
        data = request.POST
        user = User.objects.get(slug=slug)
        if request.method == "POST":
            image = request.FILES.get("image")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            mobile_number = request.POST.get("mobile_number")
            city = request.POST.get("city")
            state = request.POST.get("state")
            zip_code = request.POST.get("zip_code")

            if image:
                user.image = image
                user.first_name = first_name
                user.last_name = last_name
                user.mobile_number = mobile_number
                user.city = city
                user.state = state
                user.zip_code = zip_code
                user.profile_pic = image
                user.profile_set_up_status = True
                user.save()
                data = UserMultipleAddress.objects.create(
                    city=city, state=state, zip_code=zip_code, user_id=user.id,address_defaults="1"
                )
                data.save()
                if user.roll == "propertymanager":
                    if user.is_active == False:
                        messages.error(request, "Please verify from admin !!")
                        return redirect("/login/")
                    else:
                        messages.success(request, "profile setup successfully !!")
                        auth.login(
                            request,
                            user,
                            backend="django.contrib.auth.backends.ModelBackend",
                        )
                    return redirect("/")

                else:
                    messages.success(request, "profile setup successfully !!")
                    auth.login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    return redirect("/")
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.mobile_number = mobile_number
                user.city = city
                user.state = state
                user.zip_code = zip_code
                user.profile_set_up_status = True
            
                user.save()
                data = UserMultipleAddress.objects.create(
                    city=city, state=state, zip_code=zip_code, user_id=user.id,address_defaults="1"
                )
                data.save()
                if user.roll == "propertymanager":
                    if user.is_active == False:
                        messages.error(request, " Please verify from admin !!")
                        return redirect("/login/")
                    else:
                        messages.success(request, "profile setup successfully !!")
                        auth.login(
                            request,
                            user,
                            backend="django.contrib.auth.backends.ModelBackend",
                        )
                        return redirect("/")

                else:
                    messages.success(request, "profile setup successfully !!")
                    auth.login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    return redirect("/")

        return render(
            request,
            "web/auth/setup-profile.html",
            {"user": user, "data": data},
        )
    except:
        messages.error(request, "Something went wrong")
        return redirect("/")


# @login_required(login_url='/login/')
def login(request):

    try:
        data = request.POST
        if request.method == "POST":

            email = request.POST.get("email")

            password = request.POST.get("password")
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user:
                    if user.is_superuser == True:
                        messages.error(request, "Invalid user id and password")
                        return redirect("/login/")
                    elif (
                        user.roll == "homeowner"
                        or user.roll == "vacationer"
                        or user.roll == "propertymanager"
                    ):
                        if user.roll == "propertymanager":
                            if user.is_active == True:

                                if (
                                    user.company_status == False
                                    and user.property_manager_type == "Company"
                                ):

                                    user_auth = auth.authenticate(
                                        email=email, password=password
                                    )
                                    if user_auth:
                                        messages.error(
                                            request, "Please complete your profile"
                                        )
                                        return redirect(
                                            "/select_property_company/" + str(user.slug)
                                        )
                                    else:

                                        messages.error(
                                            request, "invalid email id or password!!!!"
                                        )
                                        return redirect("/login/")

                                if user.profile_set_up_status == False:

                                    user_auth = auth.authenticate(
                                        email=email, password=password
                                    )
                                    if user_auth:
                                        messages.error(
                                            request, "Please complete your profile"
                                        )
                                        return redirect(
                                            "/profile/setup/" + str(user.slug)
                                        )
                                    else:

                                        messages.error(
                                            request, "invalid email id or password!!!!"
                                        )
                                        return redirect("/login/")
                                else:
                                    if user.OTP:
                                        otp = generateOTP()
                                        user_type = user.roll
                                        subject = "Welcome to Honest Sherpa world"
                                        message = f"Hi {email}, thank you for registering in as a {user_type} on Honest Sherpa.Your one time password is {otp}"
                                        email_from = settings.EMAIL_HOST_USER
                                        recipient_list = email
                                        EmailThread(
                                            subject, message, [recipient_list]
                                        ).start()

                                        # send_mail(subject, message, email_from, recipient_list)
                                        user = User.objects.get(email=email)
                                        user.OTP = otp
                                        user.save()
                                        messages.success(
                                            request, "Please verify your otp !!!!"
                                        )
                                        return redirect(
                                            "/verify/sign-up/otp/" + str(user.slug)
                                        )
                                    else:
                                        user = User.objects.get(email=email)
                                        if user.check_password(password):
                                          
                                            auth.login(
                                                request,
                                                user,
                                                backend="django.contrib.auth.backends.ModelBackend",
                                            )

                                            return redirect("/")
                                        else:
                                            messages.error(request, "Password does not match")
                                            return render(
                                                request, "web/auth/login.html", {"data": data}
                                            )

                            else:
                                messages.error(request, "Please verify from admin")
                                return render(
                                    request, "web/auth/login.html", {"data": data}
                                )
                        else:
                            if user.is_active == True:
                                if user.profile_set_up_status == False:
                                    user_auth = auth.authenticate(
                                        email=email, password=password
                                    )
                                    if user_auth:
                                        messages.error(
                                            request, "Please complete your profile"
                                        )
                                        return redirect(
                                            "/profile/setup/" + str(user.slug)
                                        )
                                    else:
                                        messages.error(
                                            request, "invalid email id or password!!!!"
                                        )
                                        return redirect("/login/")
                                else:
                                    if user.OTP:
                                        otp = generateOTP()
                                        user_type = user.roll
                                        subject = "Welcome to Honest Sherpa world"
                                        message = f"Hi {email}, thank you for registering in as a {user_type} on Honest Sherpa.Your one time password is {otp}"
                                        email_from = settings.EMAIL_HOST_USER
                                        recipient_list = email
                                        EmailThread(
                                            subject, message, [recipient_list]
                                        ).start()

                                        # send_mail(subject, message, email_from, recipient_list)
                                        user = User.objects.get(email=email)
                                        user.OTP = otp
                                        user.save()
                                        messages.success(
                                            request, "Please verify your otp !!!!"
                                        )
                                        return redirect(
                                            "/verify/sign-up/otp/" + str(user.slug)
                                        )
                                    else:
                                        user_auth = auth.authenticate(
                                            email=email, password=password
                                        )
                                        if user_auth:
                                            auth.login(
                                                request,
                                                user_auth,
                                                backend="django.contrib.auth.backends.ModelBackend",
                                            )
                                            return redirect("/")
                                        else:
                                            messages.error(request, "Noooooooooooo")
                                            return render(
                                                request,
                                                "web/auth/login.html",
                                                {"data": data},
                                            )
                            else:
                                messages.error(request, "Please verify from admin")
                                return render(
                                    request, "web/auth/login.html", {"data": data}
                                )
                    else:

                        messages.error(request, "invalid email id or password!!!!")
                        return render(request, "web/auth/login.html", {"data": data})
                else:

                    messages.error(request, "Invalid email id or password!!!!")
                    return render(request, "web/auth/login.html", {"data": data})
            else:

                messages.error(request, "Invalid email id or password!!!!")
                return render(request, "web/auth/login.html", {"data": data})

        return render(request, "web/auth/login.html")

    except:

        messages.error(request, "Invalid email id or password!!!!")
        return render(request, "web/auth/login.html", {"data": data})


@login_required(login_url="/login/")
def logout(request):
    auth.logout(request)
    return redirect("/login/")


def forgot_password(request):
    try:
        if request.method == "POST":
            data = request.POST
            email = request.POST.get("email")
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if (
                    user.roll == "homeowner"
                    or user.roll == "vacationer"
                    or user.roll == "propertymanager"
                ):

                    otp = generateOTP()
                    user.OTP = otp
                    user.save()
                    subject = "Welcome to Honest Sherpa world"
                    message = f"Hi {email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = email
                    EmailThread(subject, message, [recipient_list]).start()

                    # send_mail(subject, message, email_from, recipient_list)
                    messages.success(request, "Please enter otp !!!!")
                    return redirect("/forgot/password/otp/" + str(user.slug))
                else:
                    messages.error(request, "Invalid email id !!!!")
                    return render(
                        request, "web/auth/forgot-password.html", {"data": data}
                    )
            else:
                messages.error(request, "Invalid email id !!!!")
                return render(request, "web/auth/forgot-password.html", {"data": data})
        return render(request, "web/auth/forgot-password.html")
    except:
        messages.error(request, "Something went wrong")
        return render(request, "web/auth/forgot-password.html", {"data": data})


def verify_forgot_password_otp(request, slug):
    try:
        user = User.objects.get(slug=slug)
        if request.method == "POST":
            otp1 = request.POST.get("otp1")
            otp2 = request.POST.get("otp2")
            otp3 = request.POST.get("otp3")
            otp4 = request.POST.get("otp4")
            Otp = str(otp1) + str(otp2) + str(otp3) + str(otp4)
            if user.OTP == Otp:
                messages.success(request, "Please enter new password !!!")
                user.OTP = ""
                user.save()
                return redirect("/reset/password/" + str(slug))

            else:
                messages.error(request, "otp does not matched")
                return redirect("/forgot/password/otp/" + str(slug))
        return render(
            request, "web/auth/forgot-password-otp-verification.html", {"slug": slug}
        )
    except:
        messages.error(request, "something went wrong")
        return redirect("/forgot/password/otp/" + str(slug))


def resend_otp(request, slug):
    try:
        user = User.objects.get(slug=slug)
        # em = email_templates.objects.get(id=3)
        if user.otp_sent_time != None:
            filter_date = str(user.otp_sent_time)[:19]
            now_plus_10 = datetime.datetime.strptime(
                str(filter_date), "%Y-%m-%d %H:%M:%S"
            ) + timedelta(minutes=5)
            if datetime.datetime.now() >= now_plus_10:
                user.otp_count = "0"
                user.otp_count = int(user.otp_count) + 1
                otp = generateOTP()
                user.OTP = otp
                user.otp_sent_time = datetime.datetime.now()
                user.save()
                subject = "Welcome to Honest Sherpa world"
                message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = user.email
                EmailThread(subject, message, [recipient_list]).start()
                # send_mail(subject, message, email_from, recipient_list)
                # sendsms(to, text)
                messages.success(request, "Otp sent successfully !!!")
                return redirect("/forgot/password/otp/" + str(slug))
            else:
                if user.otp_count >= str(3):
                    messages.error(
                        request,
                        f"You can send next otp after 5 mintues. Please try after {str(now_plus_10)[11:]}",
                    )
                    return redirect("/forgot/password/otp/" + str(slug))
                else:
                    user.otp_count = int(user.otp_count) + 1
                    otp = generateOTP()
                    user.OTP = otp
                    user.otp_sent_time = datetime.datetime.now()
                    user.save()
                    subject = "Welcome to Honest Sherpa world"
                    message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = user.email
                    EmailThread(subject, message, [recipient_list]).start()
                    # send_mail(subject, message, email_from, recipient_list)
                    # sendsms(to, text)
                    messages.success(request, "Otp sent successfully !!!")
                    return redirect("/forgot/password/otp/" + str(slug))
        else:
            otp = generateOTP()
            user.OTP = otp
            user.otp_sent_time = datetime.datetime.now()
            user.save()
            subject = "Welcome to Honest Sherpa world"
            message = f"Hi {user.email}, thank you for forgot password in as a {user.roll} on Honest Sherpa.Your one time password is {otp}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = user.email
            EmailThread(subject, message, [recipient_list]).start()
            # send_mail(subject, message, email_from, recipient_list)
            return redirect("/forgot/password/otp/" + str(slug))
    except:
        messages.error(request, "something went wrong")
        return redirect("/forgot/password/otp/" + str(slug))


def reset_password_form(request, slug):
    try:
        if request.method == "POST":
            new_password = request.POST.get("new-password")
            confirm_password = request.POST.get("confirm-new-password")
            if new_password is None:
                messages.error(request, "Please Fill Password ")
                return redirect("/reset/password/" + str(slug))
            elif new_password == confirm_password:
                user = User.objects.filter(slug=slug).update(
                    password=make_password(new_password)
                )
                messages.success(request, "Password Changed Successfully")
                return redirect("/login/")
            else:
                messages.error(request, "Password does not match")
                return redirect("/reset/password/" + str(slug))
        return render(request, "web/auth/reset-password.html")
    except:
        messages.error(request, "something went wrong")
        return redirect("/reset/password/" + str(slug))


@login_required(login_url="/login/")
def my_profile(request, slug):
    user = User.objects.get(slug=slug)
    globalseeting = GlobalSetting.objects.get(id=1)
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        mobile_number = request.POST.get("mobile_num")
        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.mobile_number = mobile_number
            user.save()
            messages.success(request, "Profile update successfully")
            return redirect("/my/profile/" + str(slug))
        else:
            messages.error(request, "User not found")
            return redirect("/my/profile/" + str(slug))

    return render(
        request,
        "web/profile-setup/profile.html",
        {"user": user, "globalseeting": globalseeting},
    )


@login_required(login_url="/login/")
def update_profile_pic(request, slug):
    user = User.objects.get(slug=slug)
    if request.method == "POST":
        image = request.FILES.get("image")
        if user:
            user.profile_pic = image
            user.save()
            messages.success(request, "Image update successfully")
    return redirect("/my/profile/" + str(slug))


@login_required(login_url="/login/")
def change_password(request, slug):
    user = User.objects.get(slug=slug)
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")
        check = user.check_password(old_password)
        if user:
            if check == True:
                checkNew_password = user.check_password(new_password)
                if checkNew_password == True:
                    messages.error(request, "You are already used this password")
                    return redirect("/change/password/" + str(slug))
                elif new_password == confirm_new_password:
                    user.password = make_password(new_password)
                    user.save()
                    auth.login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    messages.success(request, "Profile update successfully")
                    return redirect("/change/password/" + str(slug))
            else:
                messages.error(request, "Old password does not match")
                return redirect("/change/password/" + str(slug))
        else:
            messages.error(request, "User not found")
            return redirect("/change/password/" + str(slug))

    return render(request, "web/profile-setup/change-password.html", {"user": user})


def category(request):
    category = ProductCategory.objects.all()
    globalseeting = GlobalSetting.objects.get(id=1)
    return render(
        request,
        "web/category/select-category.html",
        {"category": category, "globalseeting": globalseeting},
    )


def category_list(request, slug):

    category = ProductCategory.objects.get(slug=slug)
    pincode = request.session.get("pin_code")
    product = Product.objects.filter(category_id=category.id)

    product_count = Product.objects.all().count()
    globalseeting = GlobalSetting.objects.get(id=1)
    like_product = []
    fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
    option_list = []
    add_to_cart_product_list = []
    for i in fav_product:
        like_product.append(i.product_id)
    for i in product:
        option = ProductOptions.objects.filter(product_id=i.id)
        for x in option:
            option_list.append(x)
        add_to_cart_product = AddToCart.objects.filter(
            user_id=request.user.id, product_id=i.id
        )
        if add_to_cart_product:
            add_to_cart_product_list.append(i.id)
    # product_price = FranchisePinCodesPrice.objects.filter(pin_code=pincode)
    globalseeting = GlobalSetting.objects.get(id=1)
    product_count = Product.objects.filter(category_id=category.id).count()
    # pin_code = FranchisePinCodes.objects.all()
    # pin_code_id=pin_code[0].id
    # pin_code_price = FranchisePinCodes.objects.get(id=pin_code_id)
    pin_code=request.session.get("pin_code")
    if request.user.is_authenticated:
        
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code, user_type=request.user.roll)
    else:
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code, user_type="vacationer")
    return render(
        request,
        "web/category/viewall_category_listing.html",
        {
            "product": product,
            "product_count": product_count,
            "category": category,
            "globalseeting": globalseeting,
            "option": option_list,
            "add_cart": add_to_cart_product_list,
            "fav_product": like_product,
            'product_price':product_price
        },
    )


def view_all_product_listing(request):
    pincode = request.session.get("pin_code")
    product = Product.objects.filter(is_active=True)
    product_count = Product.objects.all().count()
    globalseeting = GlobalSetting.objects.get(id=1)
    like_product = []
    fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
    option_list = []
    add_to_cart_product_list = []
    for i in fav_product:
        like_product.append(i.product_id)
    for i in product:
        option = ProductOptions.objects.filter(product_id=i.id)
        for x in option:
            option_list.append(x)
        add_to_cart_product = AddToCart.objects.filter(
            user_id=request.user.id, product_id=i.id
        )
        if add_to_cart_product:
            add_to_cart_product_list.append(i.id)
    # product_price = FranchisePinCodesPrice.objects.filter(pin_code=pincode)
    # pin_code = FranchisePinCodes.objects.all()
    # pin_code_id=pin_code[0].id
    # pin_code_price = FranchisePinCodes.objects.get(id=pin_code_id)
    pin_code=request.session.get("pin_code")
    if request.user.is_authenticated:
        
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code, user_type=request.user.roll)
    else:
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=product, pin_code=pin_code, user_type="vacationer")
    return render(
        request,
        "web/category/productlisting_anycategory.html",
        {
            "product": product,
            "globalseeting": globalseeting,
            "product_count": product_count,
            "option": option_list,
            "add_cart": add_to_cart_product_list,
            "fav_product": like_product,
            "product_price":product_price
        },
    )


def featured_all_product_listing(request):
    pincode = request.session.get("pin_code")
    feature_product = Product.objects.filter(is_active=True, is_feature=True)
    product_count = Product.objects.all().count()
    globalseeting = GlobalSetting.objects.get(id=1)
    like_product = []
    fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
    option_list = []
    add_to_cart_product_list = []
    for i in fav_product:
        like_product.append(i.product_id)
    for i in feature_product:
        option = ProductOptions.objects.filter(product_id=i.id)
        for x in option:
            option_list.append(x)
        add_to_cart_product = AddToCart.objects.filter(
            user_id=request.user.id, product_id=i.id
        )
        if add_to_cart_product:
            add_to_cart_product_list.append(i.id)
    # product_price = FranchisePinCodesPrice.objects.filter(pin_code=pincode)
    # pin_code = FranchisePinCodes.objects.all()
    # pin_code_id=pin_code[0].id
    # pin_code_price = FranchisePinCodes.objects.get(id=pin_code_id)
    pin_code=request.session.get("pin_code")
    if request.user.is_authenticated:
        
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=feature_product, pin_code=pin_code, user_type=request.user.roll)
    else:
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=feature_product, pin_code=pin_code, user_type="vacationer")
    return render(
        request,
        "web/category/featured_listing.html",
        {
            "product": feature_product,
            "product_count": product_count,
            "globalseeting": globalseeting,
            "option": option_list,
            "add_cart": add_to_cart_product_list,
            "fav_product": like_product,
            "product_price":product_price 
        },
    )


def ProductDetails(request, slug):
    product = Product.objects.get(slug=slug)    
    globalseeting = GlobalSetting.objects.get(id=1)
    products = Product.objects.filter(is_active=True)
    session_product_list = []
    if request.session.has_key("id"):
        if product.id in request.session["id"]:
            pass
        else:
            prod = request.session["id"]
            prod.append(product.id)
            request.session["id"] = prod
            session_product = Product.objects.filter(id__in=prod)
            session_product_list.append(session_product)
    else:
        request.session["id"] = [product.id]
    option_list = []
    add_to_cart_product_list = []
    for i in products:
        option = ProductOptions.objects.filter(product_id=i.id)
        for x in option:
            option_list.append(x)
        add_to_cart_product = AddToCart.objects.filter(
            user_id=request.user.id, product_id=i.id
        )
        if add_to_cart_product:
            add_to_cart_product_list.append(i.id)
    related_product = Product.objects.filter(is_active=True, category=product.category)
    like_product = []
    fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
    for i in fav_product:
        like_product.append(i.product_id)
    avg = ProductReviewRating.objects.filter(product_id=product).aggregate(
        avg_rating=Avg("rating")
    )
    res = dict()
    for key in avg:
        res[key] = round(avg[key], 0) if avg[key] else 0
        product.average_rating = res[key]
        product.save()
    review_datas = ProductReviewRating.objects.filter(product_id=product).order_by("-id")
    is_user_commented = review_datas.filter(user_id=request.user.id, product_id=product).exists()
    review_data=ProductReviewRating.objects.filter(product_id=product).count()
    p = Paginator(review_datas, 5)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    # pin_code = FranchisePinCodes.objects.all()
    # pin_code_id=pin_code[0].id
    # pin_code_price = FranchisePinCodes.objects.get(id=pin_code_id)
    pin_code=request.session.get("pin_code")
    if request.user.is_authenticated:
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=products, pin_code=pin_code, user_type=request.user.roll)
        price = FranchisePinCodesPrice.objects.filter(product_id = product.id, pin_code=pin_code, user_type=request.user.roll)
    else:
        product_price = FranchisePinCodesPrice.objects.filter(product_id__in=products, pin_code=pin_code,user_type="vacationer")
        price = FranchisePinCodesPrice.objects.filter(product_id = product.id, pin_code=pin_code,user_type="vacationer")
    return render(
        request,
        "web/product/product-details.html",
        {
            "product": product,
            "option": option_list,
            "related_product": related_product,
            "fav_product": like_product,
            "session_product_list": session_product_list,
            "add_cart": add_to_cart_product_list,
            "globalseeting": globalseeting,
            "product_rating":res[key],
            "review_data":review_data,
            "review_datas":review_datas,
            'is_user_commented': is_user_commented,"page_obj":page_obj,
            "product_price":product_price,
            "price":price
        },
    )


@login_required(login_url="/login/")
def productFavourite(request):
    if request.method == "POST":
        is_favourite = request.POST.get("is_favourite")
        is_product = request.POST.get("is_product")
        user = request.POST.get("user")
        if ProductFavourite.objects.filter(user_id=user, product_id=is_product):
            fav = ProductFavourite.objects.filter(user_id=user, product_id=is_product)
            fav.delete()
            return JsonResponse(
                {
                    "status": "error",
                    "message": " no changed !!!!",
                },
                status=404,
            )
        ProductFavourite.objects.create(
            user_id=user, product_id=is_product, is_favourite=True
        )
        return JsonResponse(
            {
                "status": "success",
                "message": "Product  Like Successfully !!!!",
            },
            status=200,
        )
    return JsonResponse(
        {
            "status": "error",
            "message": " no changed !!!!",
        },
        status=404,
    )


@login_required(login_url="/login/")
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        user = request.POST.get("user")

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        seven_days = datetime.date.today() + datetime.timedelta(days=7)
        product_return=Product.objects.filter(id=product_id)
 
        rate=FranchisePinCodesPrice.objects.filter(user_type=request.user.roll,product_id=product_id, pin_code=request.session.get("pin_code"))

        

        if AddToCart.objects.filter(user_id=user, product_id=product_id):
            messages.success(request, "Sucessfully add to cart!!!!")
            return redirect("/cart/items")

        else:
            for ret in product_return:
             
                offeradd=AddToCart.objects.filter(user_id=user,product__category_id=ret.category_id).exclude(product_id=product_id)
                for r in rate:
                    if not ret.is_return == False:
                        if request.user.roll == "propertymanager":
                            datas=AddToCart.objects.create(user_id=user, product_id=ret.id,delivery_date=tomorrow,return_date=seven_days
                        ,product_total_price=r.zero_seven_days_wholesale,date_diffrence="7")
                            for offercreate in offeradd:
                               if offercreate.product.category_id == datas.product.category_id:
                                    if offercreate.offer_id:
                                        AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(offer_id=offercreate.offer_id)

                                        product_price=r.zero_seven_days_wholesale
                                        discount=offercreate.offer.offer_discount
                                        discount_price=round(float(product_price)*(float(discount)/100),2)
                                        AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(product_discount=discount_price)


                      
                        elif request.user.roll == "vacationer":
                            datas=AddToCart.objects.create(user_id=user, product_id=ret.id,delivery_date=tomorrow,return_date=seven_days
                        ,product_total_price=r.zero_seven_days,date_diffrence="7")
                            for offercreate in offeradd:
                               if offercreate.product.category_id == datas.product.category_id:
                                    if offercreate.offer_id:
                                        AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(offer_id=offercreate.offer_id)
                                        product_price=r.zero_seven_days
                                        discount=offercreate.offer.offer_discount
                                        discount_price=round(float(product_price)*(float(discount)/100),2)
                                        AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(product_discount=discount_price)

                        elif request.user.roll == "homeowner":
                            da=AddToCart.objects.create(user_id=user, product_id=ret.id,delivery_date=tomorrow,return_date=seven_days
                        ,product_total_price=r.zero_seven_days,date_diffrence="7")
                            for offercreate in offeradd:
                               if offercreate.product.category_id == da.product.category_id:
                                    if offercreate.offer_id:
                                        AddToCart.objects.filter(user_id=user,product_id=da.product_id,product__category_id=ret.category_id,).update(offer_id=offercreate.offer_id)
                                        product_price=r.zero_seven_days
                                        discount=offercreate.offer.offer_discount
                                        discount_price=round(float(product_price)*(float(discount)/100),2)
                                        AddToCart.objects.filter(user_id=user,product_id=da.product_id,product__category_id=ret.category_id,).update(product_discount=discount_price)

                    else:
                        datas=AddToCart.objects.create(user_id=user, product_id=ret.id,delivery_date=tomorrow,product_total_price=r.sale_price,date_diffrence="7")
                        for offercreate in offeradd:
                            if offercreate.product.category_id == datas.product.category_id:
                                if offercreate.offer_id:
                                    AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(offer_id=offercreate.offer_id)
                                    product_price=r.sale_price
                                    discount=offercreate.offer.offer_discount
                                    discount_price=round(float(product_price)*(float(discount)/100),2)
                                    AddToCart.objects.filter(user_id=user,product_id=datas.product_id,product__category_id=ret.category_id,).update(product_discount=discount_price)

       
        return JsonResponse(
            {
                "status": "success",
                "message": "Sucessfully add to cart!!!!",
            },
            status=200,
        )
    return JsonResponse(
        {
            "status": "error",
            "message": "something went wrong!!!!",
        },
        status=404,
    )


@login_required(login_url="/login/")
def add_to_cart_ajax(request):
    if request.method == "POST":
        prod = request.POST.get("prod_id")
        user = request.POST.get("user_id")
        qty = request.POST.get("qty")        
        rate=FranchisePinCodesPrice.objects.filter(user_type=request.user.roll,product_id=prod, pin_code=request.session.get("pin_code"))
        w=AddToCart.objects.filter(user_id=user, product_id=prod)
        check_quantity=Product.objects.get(id=prod)

        if int(check_quantity.quantity) >= int(qty):
            for re in rate:    
                for r in w:
                    date_deff=int(r.date_diffrence) - 7
                    if date_deff == 0:
                        if request.user.roll == "propertymanager":
                        
                            if AddToCart.objects.filter(user_id=user, product_id=prod):
                                if not r.return_date:
                                    price=(re.sale_price)
                                    total=(float(price))*(float(qty))
                                    total_round=round(total,2)
                                    if r.offer_id != None:
                                        discount_price=float(total_round)*(float(r.offer.offer_discount)/100)
                                    
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round, product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round)

                                else:
                                    whole_price=(re.zero_seven_days_wholesale)
                                    total1=(float(whole_price))*(float(qty))
                                    total_round1=round(total1,2)
                                    if r.offer_id != None:
                                        discount_price=float(total_round1)*(float(r.offer.offer_discount)/100)
                                    
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, product_total_price=total_round1, 
                                        product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, product_total_price=total_round1)
                        elif re.user_type == request.user.roll:
                            if AddToCart.objects.filter(user_id=user, product_id=prod):
                                if not r.return_date:
                                    price=(re.sale_price)
                                    total=(float(price))*(float(qty))
                                    total_round=round(total,2)
                                    if r.offer_id != None:
                                        discount_price=float(total_round)*(float(r.offer.offer_discount)/100)
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round, product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round)
                                else:
                                    zero_price=(re.zero_seven_days)
                                    total1=(float(zero_price))*(float(qty))
                                    total_round1=round(total1,2)
                                    if r.offer_id != None:
                                        discount_price=float(total_round1)*(float(r.offer.offer_discount)/100)
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round1, product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=total_round1)
                    else:
                        if request.user.roll == "propertymanager":
                            if AddToCart.objects.filter(user_id=user, product_id=prod):
                                if  r.return_date:
                                    whole_price=(re.zero_seven_days_wholesale)
                                    total1=(float(whole_price))*(float(qty))
                                    greaterthen_price=float(date_deff)*float(re.greaterthan_seven_wholesale)
                                    a=float(total1)+float(greaterthen_price)
                                    b=round(a,2)
                                    if r.offer_id != None:
                                        discount_price=float(b)*(float(r.offer.offer_discount)/100)
                                    
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=b, product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, 
                                        product_total_price=b)
                        elif re.user_type == request.user.roll:
                            if AddToCart.objects.filter(user_id=user, product_id=prod):
                                if  r.return_date:
                                    zero_price=(re.zero_seven_days)
                                    total1=(float(zero_price))*(float(qty))
                                    greaterthen_price=float(date_deff)*float(re.greaterthan_seven)
                                    a=float(total1)+float(greaterthen_price)
                                    b=round(a,2)
                                    if r.offer_id != None:
                                        discount_price=round(float(b)*(float(r.offer.offer_discount)/100),2)
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, product_total_price=b, product_discount=discount_price)
                                    else:
                                        AddToCart.objects.filter(user_id=user, product_id=prod).update(quantity=qty, product_total_price=b)    
        else:
            return JsonResponse(
            {
                "status": "error",
                "message": "Quantity not available!!!",
            },
            status=200,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "Sucessfully add to cart!!!!",
            },
            status=200,
        )


@login_required(login_url="/login/")
def cart_items(request):
    try:
        add_cart_products = AddToCart.objects.filter(user_id=request.user.id)
        is_cart_have_returnable_product = add_cart_products.filter(product__is_return=True)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        seven_days = datetime.date.today() + datetime.timedelta(days=7)
        
        if is_cart_have_returnable_product.exists():
            returnable_product = is_cart_have_returnable_product.first()
        else:
            returnable_product = None

        product=Product.objects.filter(is_return="1",is_active="1")
        add_cart_products_count = add_cart_products.count()
        addresss=UserMultipleAddress.objects.filter(user_id=request.user.id)
        for i in add_cart_products:
            if i.delivery_date < tomorrow:
            
                date_update=AddToCart.objects.filter(user_id=request.user.id).update(delivery_date=tomorrow,return_date=seven_days)
    
        if addresss:
            for i in addresss:
                if i.address_apply == False:
                    address_data=UserMultipleAddress.objects.get(user_id=request.user.id, address_defaults="1")
                else:
                    address_data=UserMultipleAddress.objects.get(user_id=request.user.id, address_apply="1")
            globalseeting = GlobalSetting.objects.get(id=1)
            product_option_list = []
            for i in add_cart_products:
                options = ProductOptions.objects.filter(product_id=i.product.id)
                for x in options:
                    product_option_list.append(x)
            like_product = []
            fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
            for i in fav_product:
                like_product.append(i.product_id)
            pin_code=request.session.get("pin_code")
            user_id=request.user.id
           

            product_id=Product.objects.filter(is_active="1")
            if request.user.is_authenticated:
                product_price1 = FranchisePinCodesPrice.objects.filter(product_id__in=product_id, pin_code=pin_code, user_type=request.user.roll).values_list('product_id', flat=True)
                product_price = AddToCart.objects.filter(product_id__in=product_price1,user_id=user_id)            
                if product_price:               
                    total_price_list=[]
                    for i in product_price:
                        total_price_list.append(i.product_total_price)
                    
                    list_convert_to_str=list(map(float,total_price_list))
                    sums = round(sum(list_convert_to_str),2)
                    total_order_price=AddToCart.objects.filter(user_id=request.user.id).update(total_price=sums)
                    total_order_price1=AddToCart.objects.filter(user_id=request.user.id)
                    discount_dics= AddToCart.objects.filter(product_id__in=product_price1,user_id=user_id).aggregate(Sum('product_discount'))
                    value_in_dic=discount_dics.get('product_discount__sum')
                    offer_ids=OfferManagement.objects.filter().values_list("id",flat=True)
                    if value_in_dic != None:
                        for grand in total_order_price1:

                            grand_total=round(float(grand.total_price)-float(value_in_dic),2)
                    
                        return render(
                        request,
                        "web/cart/cart.html",
                        {
                            "add_cart_products": add_cart_products,
                            "product_option": product_option_list,
                            "fav_product": like_product,
                            "product_price": product_price,
                            "globalseeting": globalseeting,
                            "add_cart_products_count":add_cart_products_count,
                            "address_data":address_data,"product":product,
                            "is_cart_have_returnable_product": is_cart_have_returnable_product,
                            "returnable_product": returnable_product,
                            "total_order_price":total_order_price1,"value_in_dic":value_in_dic,"offer_ids":offer_ids,
                            "tomorrow":tomorrow, "seven_days":seven_days,"grand_total":grand_total
                        },
                    )
                    else:
                        for grand in total_order_price1:

                            grand_total=round(float(grand.total_price),2)
                       
                                    
                    return render(
                    request,
                    "web/cart/cart.html",
                    {
                        "add_cart_products": add_cart_products,
                        "product_option": product_option_list,
                        "fav_product": like_product,
                        "product_price": product_price,
                        "globalseeting": globalseeting,
                        "add_cart_products_count":add_cart_products_count,
                        "address_data":address_data,"product":product,
                        "is_cart_have_returnable_product": is_cart_have_returnable_product,
                        "returnable_product": returnable_product,
                        "total_order_price":total_order_price1,"value_in_dic":value_in_dic,"offer_ids":offer_ids,
                        "tomorrow":tomorrow, "seven_days":seven_days,"grand_total":grand_total
                    },
                )
            
    
            return render(
                request,
                "web/cart/cart.html",
                {
                    "add_cart_products": add_cart_products,
                    "product_option": product_option_list,
                    "fav_product": like_product,
                    "product_price": product_price,
                    "globalseeting": globalseeting,
                    "add_cart_products_count":add_cart_products_count,
                    "is_cart_have_returnable_product": is_cart_have_returnable_product,
                    "returnable_product": returnable_product,
                    "address_data":address_data,"product":product,
                    "tomorrow":tomorrow, "seven_days":seven_days
                #    "total_order_price":total_order_price1,
                },
            )
        else:
            globalseeting = GlobalSetting.objects.get(id=1)
            product_option_list = []
            for i in add_cart_products:
                options = ProductOptions.objects.filter(product_id=i.product.id)
                for x in options:
                    product_option_list.append(x)
            like_product = []
            fav_product = ProductFavourite.objects.filter(user_id=request.user.id)
            for i in fav_product:
                like_product.append(i.product_id)
            pin_code=request.session.get("pin_code")
            user_id=request.user.id
            product_id=Product.objects.filter(is_active="1")
            if request.user.is_authenticated:
                product_price1 = FranchisePinCodesPrice.objects.filter(product_id__in=product_id, pin_code=pin_code, user_type=request.user.roll).values_list('product_id' , flat=True)
                product_price = AddToCart.objects.filter(product_id__in=product_price1,user_id=user_id)
                if product_price:
                    total_price_list=[]
                    for i in product_price:
                        total_price_list.append(i.product_total_price)
                    list_convert_to_str=list(map(float,total_price_list))
                    sums = sum(list_convert_to_str)
                    total_order_price=AddToCart.objects.filter(user_id=request.user.id).update(total_price=sums)
                    total_order_price1=AddToCart.objects.filter(user_id=request.user.id) 
                    discount_dics= AddToCart.objects.filter(product_id__in=product_price1,user_id=user_id).aggregate(Sum('product_discount'))
                    value_in_dic=discount_dics.get('product_discount__sum')
                    if value_in_dic != None:
                        for grand in total_order_price1:

                            grand_total=round(float(grand.total_price)-float(value_in_dic),2)
                    
                        return render(
                        request,
                        "web/cart/cart.html",
                        {
                        "add_cart_products": add_cart_products,
                        "product_option": product_option_list,
                        "fav_product": like_product,
                        "product_price": product_price,
                        "globalseeting": globalseeting,
                        "add_cart_products_count":add_cart_products_count,
                        "is_cart_have_returnable_product": is_cart_have_returnable_product,
                        "returnable_product": returnable_product,
                        "product":product,
                        "total_order_price":total_order_price1,"value_in_dic":value_in_dic
                        ,"tomorrow":tomorrow, "seven_days":seven_days,"grand_total":grand_total
                    },
                    )
                    else:
                        for grand in total_order_price1:

                            grand_total=round(float(grand.total_price),2)
        
                    return render(
                    request,
                    "web/cart/cart.html",
                    {
                        "add_cart_products": add_cart_products,
                        "product_option": product_option_list,
                        "fav_product": like_product,
                        "product_price": product_price,
                        "globalseeting": globalseeting,
                        "add_cart_products_count":add_cart_products_count,
                        "is_cart_have_returnable_product": is_cart_have_returnable_product,
                        "returnable_product": returnable_product,
                        "product":product,
                        "total_order_price":total_order_price1,"value_in_dic":value_in_dic
                        ,"tomorrow":tomorrow, "seven_days":seven_days,"grand_total":grand_total
                    },
                )
            return render(
                request,
                "web/cart/cart.html",
                {
                    "add_cart_products": add_cart_products,
                    "product_option": product_option_list,
                    "fav_product": like_product,
                    "product_price": product_price,
                    "globalseeting": globalseeting,
                    "add_cart_products_count":add_cart_products_count,
                    "is_cart_have_returnable_product": is_cart_have_returnable_product,
                    "returnable_product": returnable_product,
                    "product":product,
                    "tomorrow":tomorrow, "seven_days":seven_days
                # "total_order_price":total_order_price1,
                },
            )
    except:
        messages.error(request,'Something went wrong')
        return redirect('/')


@login_required(login_url="/login/")
def clear_cart(request):
    cart = AddToCart.objects.filter(user_id=request.user.id)
    cart.delete()
    disc=OfferManagement.objects.filter(is_apply="1").update(is_apply="0")
    messages.success(request, "Cart items successfully removed")
    return redirect("/cart/items")


@login_required(login_url="/login/")
def delete_cart_items(request, id):
    add_cart_products = AddToCart.objects.get(id=id)
    add_cart_products.delete()
    messages.success(request, "Cart item successfully removed")
    return redirect("/cart/items")


@login_required(login_url="/login/")
def wishlist(request):
    fav_list = ProductFavourite.objects.filter(user_id=request.user.id)

    product = Product.objects.filter(is_active=True)

    globalseeting = GlobalSetting.objects.get(id=1)

    product_option_list = []
    add_to_cart_product_list = []
    for i in fav_list:
        options = ProductOptions.objects.filter(product_id=i.product.id)
        for x in options:
            product_option_list.append(x)
    for i in product:
        add_to_cart_product = AddToCart.objects.filter(
            user_id=request.user.id, product_id=i.id
        )
        if add_to_cart_product:
            add_to_cart_product_list.append(i.id)
    return render(
        request,
        "web/profile-setup/my-wishlist.html",
        {
            "fav_list": fav_list,
            "product_option": product_option_list,
            "add_cart": add_to_cart_product_list,
            "globalseeting": globalseeting,
        },
    )


@login_required(login_url="/login/")
def delete_wishlist(request, id):
    fav_list = ProductFavourite.objects.get(id=id)
    fav_list.delete()
    messages.success(request, "Remove item from wishlist")
    return redirect("/my/wishlist")


def contact_us(request):
    globalseeting = GlobalSetting.objects.get(id=1)
    if request.method == "POST":
        name = request.POST.get("name")
        user_type = request.POST.get("user_type")
        email = request.POST.get("email")
        company_name = request.POST.get("company_name")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        contact = Contact.objects.create(
            name=name,
            user_type=user_type,
            email=email,
            company_name=company_name,
            subject=subject,
            message=message,
        )
        messages.success(request, "Query sent successfully ")
        contact.save()
        return redirect("contact_us")

    return render(request, "web/contact-us.html", {"globalseeting": globalseeting})


def search_result(request):
    try:
        globalseeting = GlobalSetting.objects.get(id=1)
        category = ProductCategory.objects.all()
        if request.method == "POST":
            pin_code = request.POST.get("pin_code")
            request.session["post_pincode"] = pin_code
            products = Product.objects.all()[:10]
            search_pin_code=FranchisePinCodesPrice.objects.filter(pin_code=pin_code)
            if request.user.is_authenticated and request.user.is_superuser == "0" :
                product_counts = FranchisePinCodesPrice.objects.filter(pin_code=pin_code,user_type=request.user.roll).count()
                product_data = FranchisePinCodesPrice.objects.filter(pin_code=pin_code,user_type=request.user.roll)
            else:
                product_counts = FranchisePinCodesPrice.objects.filter(pin_code=pin_code,user_type="vacationer").count()
                product_data = FranchisePinCodesPrice.objects.filter(pin_code=pin_code,user_type="vacationer")
            context = {"product_count": product_counts,
                    "category": category,
                    "search_pin_code": search_pin_code,
                    "product_data":product_data,
                    "globalseeting":globalseeting
                    }
            return render(
                request,
                "web/search-result/search-results.html",
                context
            )
        else:          
            session_pin_code=request.session.get("post_pincode")
            search_pin_code=FranchisePinCodesPrice.objects.filter(pin_code=session_pin_code)         
            if request.user.is_authenticated:
                product_counts = FranchisePinCodesPrice.objects.filter(pin_code=session_pin_code,user_type=request.user.roll).count() 
                product_data = FranchisePinCodesPrice.objects.filter(pin_code=session_pin_code,user_type=request.user.roll)
            else:
                product_counts = FranchisePinCodesPrice.objects.filter(pin_code=session_pin_code,user_type="vacationer").count()
                product_data = FranchisePinCodesPrice.objects.filter(pin_code=session_pin_code,user_type="vacationer")
            
            context = {"product_count": product_counts,
                    "category": category,
                    "search_pin_code": search_pin_code,
                    "product_data":product_data
                    }
            return render(
                    request,
                    "web/search-result/search-results.html",context
                )
    except:
        messages.error(request, "please select valid pincode")
        return redirect("/")


def sub_category_ajax_dayanamic(request):
    if request.method == "POST":
        cat_id = request.POST.getlist("cat_id[]")
        subcategory = ProductSubCategory.objects.filter(category_id__in=cat_id)
        return render(
            request,
            "web/search-result/sub-category_sidebar.html",
            {"subcategory": subcategory},
        )


def select_user(request):
    if request.method == "POST":
        setuser = request.POST.get("setuser")
        obj = request.user
        obj.roll = setuser
        obj.save()
        return JsonResponse({"status": "success"})


def about(request):
    aboutData = AboutUs.objects.get(id=1)
    globalseeting = GlobalSetting.objects.get(id=1)
    return render(
        request,
        "web/about/about-us.html",
        {"aboutData": aboutData, "globalseeting": globalseeting},
    )


def blog_detail(request, slug):
    user = User.objects.get(is_superuser="True")
    data = Blog.objects.get(slug=slug)
    globalseeting = GlobalSetting.objects.get(id=1)
    return render(
        request,
        "web/blog_management/blog_detail.html",
        {"data": data, "globalseeting": globalseeting, "user": user},
    )


def blog_list(request):
    data = Blog.objects.all()

    globalseeting = GlobalSetting.objects.get(id=1)
    return render(
        request,
        "web/blog_management/blog_listing.html",
        {"data": data, "globalseeting": globalseeting},
    )

@login_required(login_url="/login/")
def review_rating(request):
    if request.method == "POST":
        user = request.POST.get("user_id")
        product = request.POST.get("product_id")
        rating = request.POST.get("rating")
        review = request.POST.get("review")
        data = ProductReviewRating.objects.create(
            user_id=user, product_id=product, rating=rating, review=review
        )
        data.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Review and Rating successfully Save !!!!",
            }
        )
    else:
        return JsonResponse({"status": "error"})



@login_required(login_url="/login/")
def my_address(request):
    user_address=UserMultipleAddress.objects.filter(user_id=request.user.id)
    context={"user_address":user_address}
    return render(request,'web/Address/my_address.html',context)  


@login_required(login_url="/login/")
def AddNewAddress(request):
    try:
        if request.method =="POST":
            location=request.POST.get('location')
            latitude=request.POST.get('lat')
            longitude=request.POST.get('long')
            zip_code=request.POST.get('zip_code')
            city=request.POST.get('city')
            address=request.POST.get('address')
            address_data=UserMultipleAddress.objects.create(location=location,
            latitude=latitude,
            longitude=longitude,
            address=address,
            city=city,zip_code=zip_code,user_id=request.user.id)
            messages.success(request,'Address Add successfully done!!')
            return redirect("/my_address/")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/my_address/")


@login_required(login_url="/login/")
def change_default_address(request,id):
    try:
        change=UserMultipleAddress.objects.filter(user_id=request.user.id,address_defaults='1').exclude(id=id)
        if UserMultipleAddress.objects.filter(user_id=request.user.id,address_defaults='0'):
            defaultss=UserMultipleAddress.objects.filter(user_id=request.user.id).update(address_defaults='1')
        for i in change:
            i.address_defaults='0'
            i.save()
        messages.success(request,'Status Change Suucessfully!!')
        return redirect("/my_address/")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/my_address/")

@login_required(login_url="/login/")
def Delete_Address(request,id):
    try:
        data=UserMultipleAddress.objects.get(id=id)
        data.delete()
        messages.success(request,'Delete Suucessfully Done!!')
        return redirect("/my_address/")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/my_address/")

@login_required(login_url="/login/")
def fetch_address(request):
  
    if request.method == "POST":

        user = request.POST.get("user_id")
      
        view_datass = UserMultipleAddress.objects.get(id=user)
       
        return JsonResponse(
            {
                "status": "success",
                "slug": view_datass.slug,
                "address": view_datass.address,
                "location":view_datass.location,
                "latitude": view_datass.latitude,
                "longitude": view_datass.longitude,
                "city": view_datass.city,
                "zip_code": view_datass.zip_code,
            }
        )
    else:
        pass
@login_required(login_url="/login/")
def Edit_address(request):
    try:
        if request.method =="POST":
            slug = request.POST.get("slug")
            address = request.POST.get("address")
            location = request.POST.get("searchs")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
        
            city = request.POST.get("city")
            zip_code = request.POST.get("zip_code")
            data = UserMultipleAddress.objects.get(slug=slug)
            data.address = address
            data.location = location
            data.latitude = latitude
            data.longitude = longitude
            data.city = city
            data.zip_code = zip_code
            data.save()
            messages.success(request,'Update Suucessfully Done!!')
            return redirect("/my_address/")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/my_address/")


def apply_address(request,id):
    try:
        change=UserMultipleAddress.objects.filter(user_id=request.user.id,address_apply='1').exclude(id=id)
       
        if UserMultipleAddress.objects.filter(user_id=request.user.id,address_apply='0'):
            defaultss=UserMultipleAddress.objects.filter(user_id=request.user.id).update(address_apply='1')
        for i in change:
            i.address_apply='0'
            i.save()
        messages.success(request,'Status Change Suucessfully!!')
        return redirect("/cart/items")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/my_address/")

        
def change_delivery_date(request):
    try:    
        if request.method == "POST":
            product = request.POST.getlist("product_id")
            user = request.POST.get("user_id")
            delivery = request.POST.get("delivery_date")
            return_date = request.POST.get("return_date")
            default_date_dffrence=7
            delivery_convert_date = datetime.datetime.strptime(delivery, '%Y-%m-%d').date()
            if return_date:
                return_convert_date = datetime.datetime.strptime(return_date, '%Y-%m-%d').date()
                days_diffrence=return_convert_date-delivery_convert_date
                days_diffrence_count=int('{}'.format(days_diffrence.days))
                product_return=Product.objects.filter(id__in=product)
                for i in product_return:
                    if i.is_return == False:
                        data=AddToCart.objects.filter(user_id=user,product_id=i.id).update(delivery_date=delivery)                        
                    else:
                        if days_diffrence_count < default_date_dffrence :
                            data=AddToCart.objects.filter(user_id=user,product_id=i.id).update(delivery_date=delivery,
                            return_date=return_date,date_diffrence="7")
                            rate=FranchisePinCodesPrice.objects.filter(user_type=request.user.roll,product_id=i.id, pin_code=request.session.get("pin_code"))
                            w=AddToCart.objects.filter(user_id=user, product_id=i.id)
                            for re in rate:    
                                for r in w:
                                    date_deff=int(r.date_diffrence) - 7
                                    if date_deff == 0:
                                        if request.user.roll == "propertymanager":
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                                whole_price=(re.zero_seven_days_wholesale)
                                                total1=(float(whole_price))*(float(r.quantity))
                                                total_round1=round(total1,2)
                                                if r.offer_id != None:
                                                    discount_price=round(float(total_round1)*(float(r.offer.offer_discount)/100),2)
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1 ,product_discount=discount_price)
                                                else:
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1)
                                        elif re.user_type == request.user.roll:
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                                zero_price=(re.zero_seven_days)
                                                total1=(float(zero_price))*(float(r.quantity))
                                                total_round1=round(total1,2)
                                                if r.offer_id != None:
                                                    discount_price=round(float(total_round1)*(float(r.offer.offer_discount)/100),2)
                                            
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1,product_discount=discount_price)
                                                else:
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1)            
                                    # else:
                                    #     print('ggggggggggggggggggggggggggggg')
                                    #     if request.user.roll == "propertymanager":
                                        
                                    #         if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                    #             if  r.return_date:
                                    #                 whole_price=(re.zero_seven_days_wholesale)
                                    #                 total1=(float(whole_price))*(float(r.quantity))
                                    #                 greaterthen_price=float(date_deff)*float(re.greaterthan_seven_wholesale)
                                    #                 a=float(total1)+float(greaterthen_price)
                                    #                 b=round(a,2)
                                    #                 if r.offer_id != None:
                                    #                     discount_price=round(float(b)*(float(r.offer.offer_discount)/100),2)
                                    #                     AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b,product_discount=discount_price)
                                    #                 else:
                                    #                     AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)
                                    #                     # AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)
                                    #     elif re.user_type == request.user.roll:
                                    #         if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                    #             if  r.return_date:
                                    #                 zero_price=(re.zero_seven_days)
                                    #                 total1=(float(zero_price))*(float(r.quantity))
                                    #                 greaterthen_price=float(date_deff)*float(re.greaterthan_seven)
                                    #                 a=float(total1)+float(greaterthen_price)
                                    #                 b=round(a,2)
                                    #                 if r.offer_id != None:
                                    #                     discount_price=round(float(b)*(float(r.offer.offer_discount)/100),2)
                                    #                     AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b,product_discount=discount_price)
                                    #                 else:
                                    #                     AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)          
                        else:
                            data=AddToCart.objects.filter(user_id=user,product_id=i.id).update(delivery_date=delivery,
                            return_date=return_date,date_diffrence=days_diffrence_count)
                            rate=FranchisePinCodesPrice.objects.filter(user_type=request.user.roll,product_id=i.id, pin_code=request.session.get("pin_code"))
                            w=AddToCart.objects.filter(user_id=user, product_id=i.id)
                            for re in rate:    
                                for r in w:
                                    date_deff=int(r.date_diffrence) - 7
                                
                                    if date_deff == 0:
                                        if request.user.roll == "propertymanager":
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                                whole_price=(re.zero_seven_days_wholesale)
                                                total1=(float(whole_price))*(float(r.quantity))
                                                total_round1=round(total1,2)
                                                if r.offer_id != None:
                                                        discount_price=round(float(total_round1)*(float(r.offer.offer_discount)/100),2)
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1,product_discount=discount_price)
                                                else:
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1)
                                                
                                                # AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1)
                                        elif re.user_type == request.user.roll:
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                            
                                                zero_price=(re.zero_seven_days)
                                                total1=(float(zero_price))*(float(r.quantity))
                                                total_round1=round(total1,2)
                                                if r.offer_id != None:
                                                        discount_price=round(float(total_round1)*(float(r.offer.offer_discount)/100),2)
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1,product_discount=discount_price)
                                                else:
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=total_round1)
                                    else:
                                        if request.user.roll == "propertymanager":
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                                if  r.return_date:
                                                    whole_price=(re.zero_seven_days_wholesale)
                                                    total1=(float(whole_price))*(float(r.quantity))
                                                    greaterthen_price=float(date_deff)*float(re.greaterthan_seven_wholesale)
                                                    a=float(total1)+float(greaterthen_price)
                                                    b=round(a,2)
                                                    if r.offer_id != None:
                                                        discount_price=round(float(b)*(float(r.offer.offer_discount)/100),2)
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b,product_discount=discount_price)
                                                    else:
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)
                                        elif re.user_type == request.user.roll:
                                            if AddToCart.objects.filter(user_id=user, product_id=i.id):
                                                if  r.return_date:
                                                    zero_price=(re.zero_seven_days)
                                                    total1=(float(zero_price))*(float(r.quantity))
                                                    greaterthen_price=float(date_deff)*float(re.greaterthan_seven)
                                                    a=float(total1)+float(greaterthen_price)
                                                    b=round(a,2)
                                                    if r.offer_id != None:
                                                        discount_price=round(float(b)*(float(r.offer.offer_discount)/100),2)
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b,product_discount=discount_price)
                                                    else:
                                                        AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)
                                                
                                                    AddToCart.objects.filter(user_id=user, product_id=i.id).update(quantity=r.quantity, product_total_price=b)        
                messages.success(request,'Date Change Succesfully Done !!')
                return redirect("/cart/items")
        return redirect("/cart/items")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("/cart/items")


    
def apply_offer_list(request):
    now_day=datetime.datetime.today().date()
    offer_data=OfferManagement.objects.filter(is_active=True,offer_validity__gte = now_day)
    category_list = offer_data.values_list('category_id', flat=True)
    values_data=AddToCart.objects.filter(user_id=request.user.id,product__category_id__in=category_list).values_list("offer_id",flat=True)
    return render(request,'web/offermanagement/apply-offer.html',{'offer_data':offer_data,"values_data":values_data})


def offerApply(request,id):
        datas=OfferManagement.objects.get(id=id)
        if datas.id:
            cart=AddToCart.objects.filter(user_id=request.user.id,product__category_id=datas.category_id).update(offer_id=datas.id)  
        offer_remove=AddToCart.objects.filter(user_id=request.user.id).exclude(offer_id=id)
        for i in offer_remove:
            i.offer_id=""
            i.product_discount=""
            i.save()
        data=AddToCart.objects.filter(user_id=request.user.id,product__category_id=datas.category_id)
        for j in data:
            if j.offer_id:
                price_disc=j.offer.offer_discount
                price=j.product_total_price
                discount_price=round(float(price)*(float(price_disc)/100),2)
                j.product_discount=discount_price 
                j.save()
        messages.success(request,"Offer apply successfully")        
        return redirect("/cart/items")

def removeOffer(request, id):
    remove=OfferManagement.objects.get(id=id)
    remove.is_apply=0
    remove.save()
    cart=AddToCart.objects.filter(offer_id=remove.id,user_id=request.user.id).update(offer_id="",  product_discount="")    
    messages.success(request, "remove successfully")
    return redirect("/apply/offer/list/")    


def orderCreate(request):
    try:
        template_name="web/ordermanagement/order.html"
        pincode = request.session.get("pin_code")
        address=request.POST.get("address")
        delivery=request.POST.get("delivery1")
        return_date=request.POST.get("return_date1")
        discount_value=request.POST.get("discount_value")
        actual_value=request.POST.get("actual_value")
        offer_id=request.POST.get("offer_id")  
        
        details=AddToCart.objects.filter(user_id=request.user.id)
        order_id=createorderid()
        data=[]
        if return_date:
            if offer_id:
                deta=OrderManagement.objects.filter(user_id=request.user.id,offer_id=int(offer_id)).values_list('offer_id', flat=True)
                if not  deta !=[]:
                    for i in deta:
                        a=int(offer_id)
                        if a == i:
                            messages.error(request, "You have already used this offer")
                            return redirect("/cart/items")
                        else:
                            print('3543t5y54y65u')
                            for d in details:
                                data.append({
                                        "product_id": d.product_id,
                                        "product_name":d.product.name,
                                        "product_category":d.product.category.name,
                                        "price": d.product_total_price,
                                        "product_return":d.product.is_return,
                                        "product_quantity": d.quantity
                                    })
                            if discount_value != None:
                                discount_price=round(float(actual_value)-float(discount_value),2)
                                ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=discount_price, order_created_by=request.user.roll, order_status="pending", order_return=return_date, delivery=delivery, product_details=data)
                                if ordercreate:
                                    AddToCart.objects.filter(user_id=request.user.id).delete()
                            else:
                                ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=actual_value, order_created_by=request.user.roll, order_return=return_date, order_status="pending", delivery=delivery, product_details=data)
                                if ordercreate:
                                    AddToCart.objects.filter(user_id=request.user.id).delete()
                            
                            subject = " Welcome to   Honest Sherpa world"
                            message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                            recipient_list = [request.user.email]
                            sendMail(subject, message,recipient_list)
                            return render(request, template_name) 
                else:
                    for d in details:
                            data.append({
                                    "product_id": d.product_id,
                                    "product_name":d.product.name,
                                    "product_category":d.product.category.name,
                                    "price": d.product_total_price,
                                    "product_return":d.product.is_return,
                                    "product_quantity": d.quantity
                            })
                    if discount_value != None:
                        discount_price=round(float(actual_value)-float(discount_value),2)
                        ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=discount_price, order_created_by=request.user.roll, order_status="pending", order_return=return_date, delivery=delivery, product_details=data)
                        if ordercreate:
                            AddToCart.objects.filter(user_id=request.user.id).delete()
                    else:
                        ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=actual_value, order_created_by=request.user.roll, order_return=return_date, order_status="pending", delivery=delivery, product_details=data)
                        if ordercreate:
                            AddToCart.objects.filter(user_id=request.user.id).delete()
                    
                    subject = " Welcome to   Honest Sherpa world"
                    message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                    recipient_list = [request.user.email]
                    sendMail(subject, message,recipient_list)
                    return render(request, template_name)  
                 
            else:
                for d in details:
                    data.append({
                            "product_id": d.product_id,
                            "product_name":d.product.name,
                            "product_category":d.product.category.name,
                            "price": d.product_total_price,
                            "product_return":d.product.is_return,
                            "product_quantity": d.quantity
                        })
                if discount_value != None:
                    discount_price=round(float(actual_value)-float(discount_value),2)
                    ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=discount_price, order_status="pending", order_created_by=request.user.roll, order_return=return_date, delivery=delivery, product_details=data)
                    
                    if ordercreate:
                        AddToCart.objects.filter(user_id=request.user.id).delete()
                else:
                    ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=actual_value, order_created_by=request.user.roll, order_status="pending", order_return=return_date, delivery=delivery, product_details=data)
                    if ordercreate:
                        AddToCart.objects.filter(user_id=request.user.id).delete()
                subject = " Welcome to   Honest Sherpa world"
                message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                recipient_list = [request.user.email]
                sendMail(subject, message,recipient_list)            
                return render(request, template_name)
        else:
            if offer_id:
                
                deta=OrderManagement.objects.filter(user_id=request.user.id,offer_id=int(offer_id)).values_list('offer_id', flat=True)
              
                if not deta != []:
                    
                    for i in deta: 
                        a=int(offer_id)
                        if a == i:
                            messages.error(request, "You have already used this offer")
                            return redirect("/cart/items")
                        else:
                            for d in details:
                                data.append({
                                        "product_id": d.product_id,
                                        "product_name":d.product.name,
                                        "product_category":d.product.category.name,
                                        "price": d.product_total_price,
                                        "product_return":d.product.is_return,
                                        "product_quantity": d.quantity
                                    })
                            if discount_value != None:
                                discount_price=round(float(actual_value)-float(discount_value),2)
                                ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=discount_price, order_created_by=request.user.roll, order_status="pending", order_return=return_date, delivery=delivery, product_details=data)
                                if ordercreate:
                                    AddToCart.objects.filter(user_id=request.user.id).delete()
                            else:
                                ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, discount_price=actual_value, order_created_by=request.user.roll, order_return=return_date, order_status="pending", delivery=delivery, product_details=data)
                                if ordercreate:
                                    AddToCart.objects.filter(user_id=request.user.id).delete()

                            subject = " Welcome to   Honest Sherpa world"
                            message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                            recipient_list = [request.user.email]
                            sendMail(subject, message,recipient_list)
                            return render(request, template_name)    
                else:
                   
                    for d in details:
                            data.append({
                                    "product_id": d.product_id,
                                    "product_name":d.product.name,
                                    "product_category":d.product.category.name,
                                    "price": d.product_total_price,
                                    "product_return":d.product.is_return,
                                    "product_quantity": d.quantity
                                })
                    if discount_value != None:
                        discount_price=round(float(actual_value)-float(discount_value),2)
                        ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, 
                        pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, 
                        discount_price=discount_price, order_created_by=request.user.roll, order_status="pending", 
                         delivery=delivery, product_details=data)
                        if ordercreate:
                            AddToCart.objects.filter(user_id=request.user.id).delete()
                    else:
                        ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id,
                         pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, 
                         discount_price=actual_value, order_created_by=request.user.roll, order_status="pending", delivery=delivery, product_details=data)
                        if ordercreate:
                            AddToCart.objects.filter(user_id=request.user.id).delete()

                    subject = " Welcome to   Honest Sherpa world"
                    message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                    recipient_list = [request.user.email]
                    sendMail(subject, message,recipient_list)
                    return render(request, template_name)
        
            else:
                for d in details:
                    data.append({
                            "product_id": d.product_id,
                            "product_name":d.product.name,
                            "product_category":d.product.category.name,
                            "price": d.product_total_price,
                            "product_return":d.product.is_return,
                            "product_quantity": d.quantity
                        })
                if discount_value != None:
                    discount_price=round(float(actual_value)-float(discount_value),2)
                    ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, 
                    pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, 
                    discount_price=discount_price, order_status="pending", order_created_by=request.user.roll, 
                     delivery=delivery, product_details=data)
                    
                    if ordercreate:
                        AddToCart.objects.filter(user_id=request.user.id).delete()
                else:
                    ordercreate=OrderManagement.objects.create(order_id=order_id, user_id=request.user.id, 
                    pin_code=pincode, offer_id=offer_id, Address=address , actual_price=actual_value, 
                    discount_price=actual_value, order_created_by=request.user.roll, order_status="pending", 
                    delivery=delivery, product_details=data)
                    if ordercreate:
                        AddToCart.objects.filter(user_id=request.user.id).delete()
                subject = " Welcome to   Honest Sherpa world"
                message = f"Hi {request.user.first_name} {request.user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
                recipient_list = [request.user.email]
                sendMail(subject, message,recipient_list)            
                return render(request, template_name)
    except:
        messages.error(request, "something went wrong")
        return render(request, template_name)


def myOrder(request):
    template_name="web/ordermanagement/my_order.html"
    globalseeting = GlobalSetting.objects.get(id=1)
    my_order=OrderManagement.objects.filter(user_id=request.user.id)
    product_quantity_list=[]
    for i in my_order:
        for j in i.product_details:
            product_quantity_list.append(j.get('product_quantity'))
    return render(request, template_name,{'globalseeting':globalseeting, 'my_order':my_order})

def orderDetails(request, slug):
    template_name="web/ordermanagement/order_details.html"
    globalseeting = GlobalSetting.objects.get(id=1)
    order_details=OrderManagement.objects.get(slug=slug)
    product_count=len(order_details.product_details)
    product_image_list=[]
    for i in order_details.product_details:
        product_image_list.append(i.get('product_id'))
    product_image=Product.objects.filter(id__in=product_image_list)
   
    discount=round((float(order_details.actual_price)-float(order_details.discount_price)),2)
    return render(request, template_name, {'order_details':order_details, 'discount':discount, 'product_image':product_image, 'product_count':product_count, 'globalseeting':globalseeting})


def orderCancel(request, slug):
    template_name="web/ordermanagement/order_cancel.html"
    globalseeting = GlobalSetting.objects.get(id=1)
    order_details=OrderManagement.objects.get(slug=slug)
    product_count=len(order_details.product_details)
    product_image_list=[]
    for i in order_details.product_details:
        product_image_list.append(i.get('product_id'))
    product_image=Product.objects.filter(id__in=product_image_list)
    order_details.order_status="cancel"
    order_details.save()
   
    discount=round((float(order_details.actual_price)-float(order_details.discount_price)),2)
    return render(request, template_name, {'order_details':order_details, 'discount':discount, 'product_image':product_image, 'product_count':product_count, 'globalseeting':globalseeting})



