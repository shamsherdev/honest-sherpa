from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

from django.db import models
from django.contrib import admin
from superadmin.models import *
import random
from django.core.mail import send_mail
from django.conf import settings
from superadmin.helper import *
from django.contrib.auth.hashers import MD5PasswordHasher, make_password, check_password
import calendar
from django.contrib.auth.decorators import login_required
from .helper import *


# Create your views here.
# def random_with_N_digits(n):
#     range_start = 10**(n-1)
#     range_end = (10**n)-1
#     return randint(range_start, range_end)\


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = auth.authenticate(email=email, password=password)
        if user:
            if user.roll == "franchise":
                if user.is_active == False:
                    messages.error(request, "Please verify from admin !!!!!")
                    return redirect("/franchise/")
                else:
                    auth.login(request, user)
                    messages.success(request, "login successfully !!!!!")
                    return redirect("/franchise/dashboard/")
            elif user is None:
                messages.error(request, "Invalid email and password")
                return redirect("/franchise/")
            else:
                messages.error(request, "Invalid email and password")
                return redirect("/franchise/")
        else:
            messages.error(request, "Invalid email and password")
            return redirect("/franchise/")
    return render(request, "franchise/auth/login.html")


def logouts(request):
    auth.logout(request)
    return redirect("/franchise/")


@login_required(login_url="/franchise/")
def dashboard(request):
    category_all = ProductCategory.objects.count()
    product_all = Product.objects.count()

    out_of_stock = Product.objects.filter(avaliable=False).count()
    product_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_product group by strftime("%%m",created_at);
    """
    product_count = Product.objects.raw(product_query)
    productcategory_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_productcategory group by strftime("%%m",created_at);
    """
    productcategory_count = ProductCategory.objects.raw(productcategory_query)
    i = 0
    append_in_month_name = []
    product_data = []

    while i <= 11:
        i += 1

        obj = dict()
        obj.update(
            {
                "month": calendar.month_name[i],
                "product_total": 0,
                "productcategory_total": 0,
            }
        )
        convert_in_month_name = calendar.month_name[i]
        product_data.append(obj)

    for product in product_count:
        product_data[int(product.month) - 1]["product_total"] = product.total

    for category in productcategory_count:
        product_data[int(category.month) - 1]["productcategory_total"] = category.total

    return render(
        request,
        "franchise/base/dashboard.html",
        {
            "category_count": category_all,
            "product_count": product_all,
            "product_data": product_data,
            "out_of_stock": out_of_stock,
            "notify": notify(request),
        },
    )


def franchise_forgot_password(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")

            if not email:
                messages.error(request, "Please Enter the email")
                return redirect("franchise_forgot_password")

            userobj = User.objects.get(email=email)

            # user_id=userobj.id
            if userobj.roll == "franchise":

                otp = random.randint(1000, 9999)

                userobj.OTP = otp
                userobj.save()
                subject = "Forgot Password"
                message = f"Hi  your forgot password otp is  ---  {otp}"
                email_from = "EMAIL_HOST_USER"
                recipient_list = [email]
                send_mail(subject, message, email_from, recipient_list)

                messages.success(
                    request, "Your Otp send successfully on your email id !"
                )
                return redirect("/franchise/otp/" + str(userobj.slug))
            else:
                userobj.roll != "franchise"
                messages.error(request, "Franchise User Email Does Not exist")
                return redirect("franchise_forgot_password")

    except:

        messages.error(request, "Something Went Wrong")
        return redirect("franchise_forgot_password")
    return render(request, "franchise/auth/forgot_password.html")


def otp(request, slug):

    if request.method == "POST":
        otp = request.POST.get("otp")
        user = User.objects.get(slug=slug)

        if user.OTP == otp:
            messages.success(request, " Otp Match ")
            return redirect("/franchise/reset_password/" + str(user.slug))
        else:
            messages.error(request, " Otp does not match ")
            return redirect("/franchise/otp/" + str(slug))

    return render(request, "franchise/auth/otp.html", {"slug": slug})


def resend_otp(request, slug):
    otp = generateOTP()
    try:
        data = User.objects.get(slug=slug)
        data.OTP = otp
        data.save()
        send_to = [data.email]
        subject = "Forgot Password"
        content = "This is your One Time Password " + otp
        sendMail(subject, content, send_to)
        messages.success(request, "OTP Resend Successfully !!!! ")
        return redirect("/admin/forgot-otp/" + str(slug))
    except:
        messages.error(request, "Something went wrong !!!! ")
        return redirect("/admin/forgot-otp/" + str(slug))


def reset_password(request, slug):
    try:
        if request.method == "POST":
            newpassword = request.POST.get("newpassword")
            confirmpassword = request.POST.get("confirmpassword")
            if not (
                newpassword
                and not newpassword.isspace()
                and confirmpassword
                and not confirmpassword.isspace()
            ):
                messages.error(request, "Both  Are Required")
                return redirect("/franchise/reset_password/" + str(slug))

            if newpassword == confirmpassword:
                user = User.objects.get(slug=slug)
                user.password = make_password(newpassword)
                user.OTP = ""
                user.save()
                messages.success(request, "Your Password Change Successfully Done!!")
                return redirect("logins")

    except:
        messages.error(request, "Something Went Wrong")
        return redirect("/franchise/reset_password/" + str(slug))

    return render(request, "franchise/auth/reset_password.html")


@login_required(login_url="/franchise/")
def product_list(request):
    product = Product.objects.all()
    return render(
        request,
        "franchise/productmanagement/product-list.html",
        {"product": product, "notify": notify(request)},
    )


@login_required(login_url="/franchise/")
def product_detail(request, slug):
    product = Product.objects.all()
    product_detail = Product.objects.get(slug=slug)
    product_option = ProductOptions.objects.filter(product_id=product_detail.id)
    print(product_option)

    return render(
        request,
        "franchise/productmanagement/product_detail.html",
        {
            "product_detail": product_detail,
            "product": product,
            "product_option": product_option,
        },
    )


# Franchise View profile and Change Password:


def view_profile(request, slug):
    view_profile_data = User.objects.get(slug=slug)
    try:
        if request.method == "POST":
            edit_first_name = request.POST.get("firstname")
            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact_number = request.POST.get("phonenumber")
            image = request.FILES.get("image")
            edit_country = request.POST.get("country")
            edit_state = request.POST.get("state")
            edit_city = request.POST.get("city")
            edit_pincode = request.POST.get("pincode")
           
            if not (
                edit_first_name
                and not edit_first_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_contact_number
                and not edit_contact_number.isspace()
            ):
                messages.error(request, "All Fields Are Required")
                return redirect("/franchise/view_profile/" + str(slug))
            view_profile_data.first_name = edit_first_name
            view_profile_data.last_name = edit_last_name
            view_profile_data.mobile_number = edit_contact_number
            view_profile_data.country = edit_country
            view_profile_data.state = edit_state
            view_profile_data.city = edit_city
            view_profile_data.zip_code = edit_pincode
            if image:
                view_profile_data.profile_pic = image
                view_profile_data.save()
            view_profile_data.save()
            messages.success(request, "Update Successfully Done!!")
            return redirect("/franchise/view-profile/" + str(slug))

    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/franchise/view-profile/" + str(slug))
    return render(
        request,
        "franchise/franchise_profile/view_profile.html",
        {"view_profile_data": view_profile_data},
    )


def change_password(request, slug):
    user = User.objects.get(slug=slug)
    try:
        if request.method == "POST":
            old_password = request.POST.get("oldPassword")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if old_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/franchise/change-password/" + str(slug))
            if new_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/franchise/change-password/" + str(slug))
            if confirm_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/franchise/change-password/" + str(slug))
            if check_password(old_password, user.password):
                if new_password != confirm_password:
                    messages.error(request, "Password does not matched")
                    return redirect("/franchise/change-password/" + str(slug))
                user.set_password(confirm_password)
                user.save()
                auth.login(request, user)
                messages.success(request, "Password successfully changed!")
                return redirect("/franchise/change-password/" + str(slug))
            else:
                messages.error(request, "Password does not matched")
                return redirect("/franchise/change-password/" + str(slug))

    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/franchise/change-password/" + str(slug))

    return render(
        request,
        "franchise/franchise_profile/franchise_change_password.html",
        {"change_password_data": user},
    )


# End Franchise View Profile and Change Password:

# def notification(request):
#     return render(request,"franchise/base/dashboard.html")


def request_products(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        user_id = request.POST.get("user_id")
        quantity = request.POST.get("quantity")
        data = Product.objects.get(id=product_id)
        product_quantity = data.quantity
        if int(quantity) > product_quantity:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "please select quantity less than !!!!",
                    "quantity": product_quantity,
                },
                status=404,
            )

        else:
            data = RequestProduct.objects.create(
                product_id=product_id, user_id=user_id, quantity=quantity
            )
            return JsonResponse(
                {"status": "success", "message": "Saved Successfully"},
                status=200,
            )


def approved_request_products_by_admin(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        user_id = request.POST.get("user_id")
        quantity = request.POST.get("quantity")
        data = RequestProduct.objects.get(id=product_id)
        product_quantity = data.quantity
        if int(quantity) > int(product_quantity):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "please select quantity less than !!!!",
                    "quantity": product_quantity,
                },
                status=404,
            )

        else:
            data = ApprovedProductByAdmin.objects.create(
                product_id=product_id, user_id=user_id, quantity=quantity
            )
            return JsonResponse(
                {"status": "success", "message": "Saved Successfully"},
                status=200,
            )


def my_product_list(request):

    product = ApprovedProductByAdmin.objects.filter(user_id=request.user.id)

    return render(
        request, "franchise/productmanagement/myproductlist.html", {"product": product}
    )


@login_required(login_url="/franchise/")
def orderList(request):
    template_name="franchise/ordermanagement/order_list.html"
    product = OrderManagement.objects.all()
    product_zip_codes = product.values_list('pin_code', flat=True)
    franchise_name=FranchisePinCodes.objects.filter(pin_code__in=product_zip_codes, user_id=request.user.id )
    franchise_pin_codes = franchise_name.values_list('pin_code', flat=True)
    order_list=OrderManagement.objects.filter(pin_code__in=franchise_pin_codes).order_by('-id')

    return render(request,template_name,{"product": product, "order_list":order_list, "franchise_name":franchise_name, "notify": notify(request)})