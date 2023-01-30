import re
import geopandas
from django.http import HttpResponse, JsonResponse, request
from django.shortcuts import render, redirect
from django.shortcuts import get_list_or_404, get_object_or_404

from franchise.views import product_detail

from .models import *
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from .helper import *
from django.contrib.auth.hashers import MD5PasswordHasher, make_password, check_password
from django.conf import settings
from django.core.mail import send_mail
import calendar
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers
import threading
from threading import Thread
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from honest_app.helpers import *
import pytz
from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
import xlwt
import openpyxl
from openpyxl import Workbook
import xlrd
import pandas as pd
import numpy as np
from django.db.models import Sum


User = get_user_model()
# Create your views here.


def handler404(request, *args, **argv):
    response = render("404.html", {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("/admin/dashboard/")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = auth.authenticate(email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email and password")
            return redirect("/admin/")

        if user.is_superuser == True:
            auth.login(request, user)
            return redirect("/admin/dashboard/")

        elif user.roll == "subadmin":
            auth.login(request, user)
            return redirect("/admin/dashboard/")
        else:
            messages.error(request, "Invalid email and password")
            return redirect("/admin/")

    return render(request, "admin/auth/login.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def logout(request):
    auth.logout(request)
    return redirect("/admin/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def dashboard(request):
    customer = User.objects.filter(roll="customer").count()
    subadmin = User.objects.filter(roll="subadmin").count()
    homeowners = User.objects.filter(roll="homeowner").count()
    propertymanager = User.objects.filter(roll="propertymanager").count()
    franchise = User.objects.filter(roll="franchise").count()
    category = ProductCategory.objects.count()
    product = Product.objects.count()
    out_of_stock = Product.objects.filter(avaliable=False).count()
    customer_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_user where roll="customer" group by strftime("%%m",created_at);
    """
    customer_user_count = User.objects.raw(customer_query)
    homeowner_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_user where roll="homeowner" group by strftime("%%m",created_at);
    """
    homeowner_user_count = User.objects.raw(homeowner_query)
    propertymanager_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_user where roll="propertymanager" group by strftime("%%m",created_at);
    """
    propertymanager_user_count = User.objects.raw(propertymanager_query)

    franchise_query = f"""
        select id, count(*) as total,strftime("%%m",created_at) as month 
        from superadmin_user where roll="franchise" group by strftime("%%m",created_at);
    """
    franchise_user_count = User.objects.raw(franchise_query)

    i = 0
    append_in_month_name = []
    customer_data = []

    while i <= 11:
        i += 1

        obj = dict()
        obj.update(
            {
                "customer_total": 0,
                "month": calendar.month_name[i],
                "homeowner_total": 0,
                "propertymanager_total": 0,
                "franchise_total": 0,
            }
        )
        convert_in_month_name = calendar.month_name[i]
        customer_data.append(obj)

    for user in customer_user_count:
        customer_data[int(user.month) - 1]["customer_total"] = user.total

    for user in homeowner_user_count:
        customer_data[int(user.month) - 1]["homeowner_total"] = user.total

    for user in propertymanager_user_count:
        customer_data[int(user.month) - 1]["propertymanager_total"] = user.total

    for user in franchise_user_count:
        customer_data[int(user.month) - 1]["franchise_total"] = user.total

    return render(
        request,
        "admin/basic/dashboard.html",
        {
            "customer": customer,
            "subadmin": subadmin,
            "homeowners": homeowners,
            "propertymanager": propertymanager,
            "franchise": franchise,
            "category": category,
            "product": product,
            "out_of_stock": out_of_stock,
            "customer_data": customer_data,
        },
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def subadmin(request):
    subadmin = User.objects.filter(roll="subadmin")
    return render(request, "admin/event/subadmin.html", {"subadmin": subadmin})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_subadmin(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            number = request.POST.get("number")
            subadmin = request.POST.get("subadmin")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zipcode = request.POST.get("zipcode")
            image = request.FILES.get("image")
            status = request.POST.get("status")

            permission = request.POST.getlist("name[]")

            password = generatePassword()

            data = User.objects.create(
                first_name=name,
                email=email.lower(),
                mobile_number=number,
                roll=subadmin,
                password=make_password(password),
                is_active=status,
                time_zone=timezone,
                identification_number=identification_number,
                manager=manager,
                description=description,
                department=department,
                profile_pic=image,
                fax=fax,
            )
            data.save()
            address_data = UserMultipleAddress.objects.create(
                city=city,
                country=country,
                address=address,
                zip_code=zipcode,
                state=state,
                user_id=data.id,
            )
            address_data.save()

            current_url = settings.SITE_URL

            subject = "Welcome to Honest Sherpa world"
            message = f'Hi {name}, thank you for registering in as a customer on Honest Sherpa. Please <a href="{current_url}">Login Here</a>, Your Email Id is --- {email}  Your password is ---  {password}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(subject, message, email_from, recipient_list)
            for i in permission:
                user = User.objects.get(id=data.id)
                user.user_permissions.add(i)
            messages.success(
                request,
                "Sub admin added successfully !!!!!",
            )
            return redirect("/admin/customer-view/")
            # send_to = [email]
            # subject = "Your Password is Here "
            # content = "Hi" + name + " Your Zenerated Password is  " + generatePassword()
            # sendMail(subject, content, send_to)
        else:
            userdata = User.objects.all()
            content = ContentType.objects.all()
            model_list = [
                "dashboard",
                "user",
                "faq",
                "appbanners",
                "productcategory",
                "product",
                "enquiry",
                "globalsettings",
                # "testimonial",
                "email",
                "offermanagement",
                "requestproducts",
                "productsubcategory",
                "reports",
                # "coupon",
                "cms",
                "aboutuspage" "product_option",
                "options_value",
            ]

            list_1 = list()
            for i in content:

                if i.model in model_list:
                    list_1.append(i.id)
                else:
                    pass
            list_2 = list()
            for i in list_1:
                per = Permission.objects.filter(content_type_id=i)
                x = list()
                c = 1
                for i in per:
                    if c == 1:
                        s_name = i.content_type.model.split("_")
                        if len(s_name) > 1:
                            s = ""
                            for name in s_name:
                                if name == 0:
                                    s = name.title()
                                else:
                                    s = s + " " + name.title()
                            x.append(s)
                        else:
                            x.append(s_name[0].title())
                        c += 1
                    else:
                        pass

                    if "Sidebar" in i.name:
                        x.insert(1, {"Sidebar": i.id})
                    if "view" in i.name:
                        x.append({"View": i.id})
                    if "add" in i.name:
                        x.append({"Add": i.id})
                    elif "change" in i.name:
                        x.append({"Edit": i.id})
                    elif "delete" in i.name:
                        x.append({"Delete": i.id})
                    elif "download" in i.name:
                        x.append({"Download": i.id})

                try:
                    list_2.append(x)
                except:
                    pass
            timeZone = pytz.all_timezones
            return render(
                request,
                "admin/event/add-subadmin.html",
                {"list_2": list_2, "userdata": userdata, "timeZone": timeZone},
            )
    except:
        messages.error(request, "something went wrong")
        return redirect("add_subadmin")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_subadmin(request, slug):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            number = request.POST.get("number")
            subadmin = request.POST.get("subadmin")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zipcode = request.POST.get("zipcode")
            image = request.FILES.get("image")
            status = request.POST.get("status")
            permission = request.POST.getlist("name[]")
            user = User.objects.get(slug=slug)
            edit = UserMultipleAddress.objects.filter(user_id=user.id)

            user.first_name = name
            user.email = email.lower()
            user.mobile_number = number
            user.is_active = status
            user.time_zone = timezone
            user.manager = manager
            user.identification_number = identification_number
            user.department = department
            user.description = description
            user.fax = fax
            if image:
                user.profile_pic = image
            user.save()
            if edit:
                for edit_address in edit:
                    edit_address.address = address
                    edit_address.country = country
                    edit_address.state = state
                    edit_address.city = city
                    edit_address.zip_code = zipcode
                    edit_address.save()
            else:
                data = UserMultipleAddress.objects.create(
                    address=address,
                    country=country,
                    state=state,
                    city=city,
                    zip_code=zipcode,
                    user_id=user.id,
                )
            user.user_permissions.clear()
            for i in permission:
                user = User.objects.get(slug=slug)
                user.user_permissions.add(i)
            messages.success(request, " Subadmin is Update Successfully !!!")
            return redirect("/admin/details/" + str(slug))
        else:
            users = User.objects.filter(slug=slug)
            userdata = User.objects.all()
            try:
                u = User.objects.get(slug=slug)
            except:
                messages.error(request, " Subadmin is created Failed !")
                return redirect("/admin/edit_subadmin/" + slug)

            c = ContentType.objects.all()
            model_list = [
                "dashboard",
                "user",
                "faq",
                "appbanners",
                "productcategory",
                "product",
                "enquiry",
                "globalsettings",
                # "testimonial",
                "email",
                "offermanagement",
                "requestproducts",
                "productsubcategory",
                "reports",
                # "coupon",
                "cms",
                "aboutuspage" "product_option",
                "options_value",
            ]

            list_1 = []
            for i in c:

                if i.model in model_list:
                    list_1.append(i.id)
                else:
                    pass

            l1 = []

            for i in list_1:

                per = Permission.objects.filter(content_type_id=i)

                x = []
                c = 1
                for i in per:
                    if c == 1:
                        s_name = i.content_type.model.split("_")
                        if len(s_name) > 1:
                            s = ""
                            for name in s_name:
                                if name == 0:
                                    s = name.title()
                                else:
                                    s = s + " " + name.title()
                            x.append(s)
                        else:
                            x.append(s_name[0].title())

                        c += 1
                    else:
                        pass
                    if "Sidebar" in i.name:
                        x.insert(1, {"Sidebar": i.id})
                    elif "view" in i.name:
                        x.append({"View": i.id})
                    elif "add" in i.name:
                        x.append({"Add": i.id})
                    elif "change" in i.name:
                        x.append({"Edit": i.id})
                    elif "delete" in i.name:
                        x.append({"Delete": i.id})
                    elif "download" in i.name:
                        x.append({"Download": i.id})
                try:
                    l1.append(x)
                except:
                    pass

            permission_id = u.user_permissions.filter(user__slug=slug)
            l = []
            for i in permission_id:
                l.append(i.id)
            subadmin = User.objects.get(slug=slug)

            edit_addres = UserMultipleAddress.objects.filter(user_id=subadmin.id)
            timeZone = pytz.all_timezones

        return render(
            request,
            "admin/event/edit-subadmin.html",
            {
                "subadmin": subadmin,
                "users": users,
                "userdata": userdata,
                "l": l1,
                "list": l,
                "edit_address": edit_addres,
                "timeZone": timeZone,
            },
        )
    except:
        messages.error(request, "Something went wrong")
        return redirect("edit_subadmin/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_subadmin(request, id):
    data = User.objects.get(id=id)
    data.delete()
    return redirect("/admin/subadmin/")


# Customer Registration CURD :
# customer register/ Add customer  by admin :


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def customer_registration(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("firstname")
            last_name = request.POST.get("lastname")
            email = request.POST.get("email")
            contact_number = request.POST.get("contactnumber")
            is_active = request.POST.get("is_active")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zipcode = request.POST.get("zipcode")
            image = request.FILES.get("image")
            password = generatePassword()
            if User.objects.filter(email=email).exists():

                messages.error(request, "Email already exists")
                return redirect("customer_registration")
            if not (
                first_name
                and not first_name.isspace()
                and last_name
                and not last_name.isspace()
                and email
                and not email.isspace()
                and contact_number
                and not contact_number.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("customer_registration")

            registration_data = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email.lower(),
                roll="vacationer",
                is_active=is_active,
                mobile_number=contact_number,
                time_zone=timezone,
                identification_number=identification_number,
                manager=manager,
                description=description,
                department=department,
                profile_pic=image,
                fax=fax,
                is_verified=True,
                password=make_password(password),
            )
            registration_data.save()
            address_data = UserMultipleAddress.objects.create(
                city=city,
                country=country,
                address=address,
                zip_code=zipcode,
                state=state,
                user_id=registration_data.id,
            )
            address_data.save()
            subject = " Welcome to   Honest Sherpa world"
            message = f"Hi {first_name}, Thank you for  registering  on Honest Sherpa . Your Email is {email} and Your password is ---  {password}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)

            messages.success(request, "Customer successfully registerted!")
            return redirect("customer_view")

    except:
        messages.error(request, "Something went wrong ")
        return redirect("customer_registration")
    timeZone = pytz.all_timezones

    # {% if HideShow.sr == True %} checked {% endif %}
    return render(
        request, "admin/UserManagement/customer_register.html", {"timeZone": timeZone}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def customer_view(request):
    view_data = User.objects.all().exclude(is_superuser=True).order_by("-id")
    HideShow = UserDataHideShow.objects.get(id=1)
    return render(
        request,
        "admin/UserManagement/customer_view.html",
        {"view_data": view_data, "HideShow": HideShow},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def details(request, slug):
    view_data = User.objects.get(slug=slug)
    view_datass = UserMultipleAddress.objects.filter(user_id=view_data.id)
    zip_codes_list = view_datass.values_list("zip_code", flat=True)

    user_address = view_datass.filter(user_id=view_data.id).order_by("id").first()
    if user_address and view_data.roll in ["homeowner", "propertymanager"]:
        zipcodedata = FranchisePinCodesPrice.objects.filter(
            pin_code__in=zip_codes_list,
            user_type=view_data.roll,
            pin_code=user_address.zip_code,
        ).first()
    else:
        zipcodedata = None

    return render(
        request,
        "admin/UserManagement/details.html",
        {
            "view_data": view_data,
            "view_datass": view_datass,
            "zipcodedata": zipcodedata,
        },
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def addaddress(request, slug):
    try:
        if request.method == "POST":
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zip_code = request.POST.get("zip_code")
            user = request.POST.get("user")

            data = UserMultipleAddress.objects.create(
                address=address,
                country=country,
                state=state,
                city=city,
                zip_code=zip_code,
                user_id=user,
            )
            data.save()
            messages.success(request, "Address add successfully Done!!")
            return redirect("/admin/details/" + str(slug))
        else:
            pass
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/details/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def fetch_address(request):
    if request.method == "POST":

        user = request.POST.get("user_id")
        view_datass = UserMultipleAddress.objects.get(id=user)

        return JsonResponse(
            {
                "status": "success",
                "slug": view_datass.slug,
                "address": view_datass.address,
                "country": view_datass.country,
                "state": view_datass.state,
                "city": view_datass.city,
                "zip_code": view_datass.zip_code,
            }
        )
    else:
        pass


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_address(request):
    try:
        if request.method == "POST":
            slug = request.POST.get("slug")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zip_code = request.POST.get("zip_code")
            data = UserMultipleAddress.objects.get(slug=slug)
            data.address = address
            data.country = country
            data.state = state
            data.city = city
            data.zip_code = zip_code
            data.save()
            messages.success(request, "Address Update Successfully Done!!")
            return redirect("/admin/details/" + data.user.slug)
    except:
        messages.error(request, "Something Went Wrong !!")
        return redirect("/admin/details/" + data.user.slug)


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_address(request, id):
    data = UserMultipleAddress.objects.get(id=id)
    data.delete()
    messages.error(request, "Address Delete Successfully Done!!")
    return redirect("/admin/details/" + data.user.slug)


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def user_address_delete(request, id):
    view_data = User.objects.get(id=id)
    view_data.delete()
    messages.error(request, "Address Delete Successfully Done!!")
    return redirect("/admin/details/" + view_data.slug)


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def user_detail_status(request, slug):
    try:
        view_data = User.objects.get(slug=slug)
        if request.method == "POST":
            status = request.POST.get("status")
            reason = request.POST.get("reason")
            if view_data.is_active == 1:
                if not (reason and not reason.isspace()):
                    messages.error(request, "Please Enter the reason")
                    return redirect("/admin/user_detail_status/" + str(slug))
            if status == "True":
                view_data.is_active = False
                view_data.reason = reason
                subject = "Your Account is Deactivate"
                message = f"Hello {view_data.first_name} user your account is deactivate due to this reason:{reason}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [view_data.email]
                # send_mail(subject, message, email_from, recipient_list)
                EmailThread(subject, message, recipient_list).start()

            else:
                view_data.is_active = True
                view_data.reason = ""
                subject = "Your Account is activate"
                message = f"Hello {view_data.first_name} user your account is activate "
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [view_data.email]
                EmailThread(subject, message, recipient_list).start()
            view_data.save()
            messages.success(request, "Status Changed Successfully")
            return redirect("/admin/details/" + str(slug))
    except:
        messages.error(request, "Something Went Wrong")
        return redirect("/admin/details/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def whole_sale_status(request, slug):
    view_data = User.objects.get(slug=slug)
    if request.method == "POST":
        weeklyprice = request.POST.get("wholsesale")

        user = request.POST.get("user")

        is_enable = request.POST.get("is_enable")

        if is_enable:
            view_data.wholesale_price_status = is_enable
            data = WholeSalePriceData.objects.create(
                user_id=user, pincode_wholesale_price_id=weeklyprice
            )
        else:
            view_data.wholesale_price_status = 0
        view_data.save()

    return redirect("/admin/details/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def propertymanager_negotiable_status(request, slug):
    view_data = User.objects.get(slug=slug)
    if request.method == "POST":
        user = request.POST.get("user")
        is_negotiable = request.POST.get("is_negotiable")
        if is_negotiable:
            view_data.propertymanager_negotiable = is_negotiable

        else:
            view_data.propertymanager_negotiable = 0
        view_data.save()

    return redirect("/admin/details/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def customer_edit(request, slug):
    try:
        edit_data = User.objects.get(slug=slug)
        edit = UserMultipleAddress.objects.filter(user_id=edit_data.id)
        if request.method == "POST":
            edit_fisrt_name = request.POST.get("firstname")
            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact = request.POST.get("contact_number")
            edit_is_active = request.POST.get("is_active")
            edit_timezone = request.POST.get("timezone")

            edit_manager = request.POST.get("manager")
            edit_identification_number = request.POST.get("identification_number")
            edit_department = request.POST.get("department")
            edit_description = request.POST.get("description")
            edit_fax = request.POST.get("fax")
            edit_addres = request.POST.get("address")

            edit_country = request.POST.get("country")
            edit_state = request.POST.get("state")
            edit_city = request.POST.get("city")
            edit_zipcode = request.POST.get("zipcode")
            edit_image = request.FILES.get("image")
            if not (
                edit_fisrt_name
                and not edit_fisrt_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_email
                and not edit_email.isspace()
                and edit_contact
                and not edit_contact.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/customer_edit/" + str(slug))
            edit_data.first_name = edit_fisrt_name
            edit_data.last_name = edit_last_name
            edit_data.email = edit_email.lower()
            edit_data.mobile_number = edit_contact
            edit_data.is_active = edit_is_active
            edit_data.time_zone = edit_timezone
            edit_data.manager = edit_manager
            edit_data.identification_number = edit_identification_number
            edit_data.department = edit_department
            edit_data.description = edit_description
            edit_data.fax = edit_fax
            if edit_image:
                edit_data.profile_pic = edit_image
            edit_data.save()
            if edit:
                for edit_address in edit:

                    edit_address.address = edit_addres
                    edit_address.country = edit_country
                    edit_address.state = edit_state
                    edit_address.city = edit_city
                    edit_address.zip_code = edit_zipcode
                    edit_address.save()
            else:
                data = UserMultipleAddress.objects.create(
                    address=edit_addres,
                    country=edit_country,
                    state=edit_state,
                    city=edit_city,
                    zip_code=edit_zipcode,
                    user_id=edit_data.id,
                )

            messages.success(request, "Customer updated successfully!!")
            return redirect("/admin/details/" + str(slug))
    except:
        messages.error(request, "SomeThing Went Wrong!!")
        return redirect("/admin/customer_edit/" + str(slug))
    timeZone = pytz.all_timezones
    return render(
        request,
        "admin/UserManagement/customer_edit.html",
        {"edit_data": edit_data, "edit_address": edit, "timeZone": timeZone},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def customer_view_detail(request, slug):
    view_detail_data = User.objects.get(slug=slug)

    return render(
        request,
        "admin/UserManagement/customer_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def customer_delete(request, id):
    view_detail_data = User.objects.get(id=id)
    view_detail_data.delete()
    messages.error(request, "Customer deleted Successfully!!")
    return redirect("customer_view")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def superadmin(request):
    superadmin = User.objects.filter(roll="superadmin").order_by("-id")

    return render(
        request, "admin/UserManagement/superadmin.html", {"superadmin": superadmin}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def UserActionAjax(request):
    if request.method == "POST":
        DropdownId = request.POST.get("DropdownId")

        UserId = request.POST.getlist("userId[]")

        if DropdownId == "1":

            save_status = User.objects.filter(id__in=UserId).update(is_active=1)
            userEmail = User.objects.filter(id__in=UserId)
            for i in userEmail:
                subject = "Your Account is activate"
                message = f"Hello{i.first_name} user your account is activate "
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [i.email]
                EmailThread(subject, message, recipient_list).start()
            return JsonResponse(
                {"status": "success", "message": "Status Change Succesfully !!!"}
            )
        if DropdownId == "2":
            save_status = User.objects.filter(id__in=UserId).update(is_active=0)
            return JsonResponse(
                {"status": "success", "message": "Status Change Succesfully !!!"}
            )
        if DropdownId == "3":

            save_status = User.objects.filter(id__in=UserId).delete()
            return JsonResponse(
                {"status": "success", "message": "Status Change Succesfully !!!"}
            )
        if DropdownId == "4":
            subject = request.POST.get("subject")
            message = request.POST.get("message")
            save_status = User.objects.filter(id__in=list(UserId))
            for i in save_status:
                recipient_list = [i.email]
                EmailThread(subject, message, recipient_list).start()

            return JsonResponse(
                {"status": "success", "message": "Status Change Succesfully !!!"}
            )
    return JsonResponse(
        {"status": "success", "message": "Status Change Succesfully !!!"}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def UserFilterAjax(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type == "0":
            view_data = User.objects.filter(is_active=user_type).exclude(
                is_superuser=True
            )
            return render(
                request,
                "admin/UserManagement/user-table.html",
                {"view_data": view_data},
            )

        view_data = User.objects.filter(roll=user_type).exclude(is_superuser=True)
        return render(
            request, "admin/UserManagement/user-table.html", {"view_data": view_data}
        )
    return JsonResponse(
        {"status": "success", "message": "Status Change Succesfully !!!"}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def UserShowHideAjax(request):
    if request.method == "POST":
        colomnType = request.POST.get("arr")
        JsonColomnType = json.loads(colomnType)
        for i in JsonColomnType:

            data = UserDataHideShow.objects.get(id=1)
            if i.get("name") == "sr":

                if i.get("checked") == True:
                    data.sr = 1
                    data.save()
                else:
                    data.sr = 0
                    data.save()

            if i.get("name") == "name":

                # data.name = i.get('checked')
                # data.save()
                if i.get("checked") == True:
                    data.name = 1
                    data.save()
                else:
                    data.name = 0
                    data.save()

            if i.get("name") == "email":

                # data.email = i.get('checked')
                # data.save()
                if i.get("checked") == True:
                    data.email = 1
                    data.save()
                else:
                    data.email = 0
                    data.save()

            if i.get("name") == "roll":
                if i.get("checked") == True:
                    data.role = 1
                    data.save()
                else:
                    data.role = 0
                    data.save()

                # data.role = i.get('checked')
                # data.save()

            if i.get("name") == "action":

                # data.action = i.get('checked')
                # data.save()
                if i.get("checked") == True:
                    data.action = 1
                    data.save()
                else:
                    data.action = 0
                    data.save()

        return JsonResponse(
            {
                "status": "success",
                "message": "Status Change Succesfully !!!",
            }
        )

    return JsonResponse(
        {"status": "success", "message": "Status Change Succesfully !!!"}
    )


# def UserShowHideAjax2(request):
#     if request.method == "POST":
#         colomnType = request.POST.get('arr')
#         JsonColomnType = json.loads(colomnType)
#         for i in JsonColomnType:
#             data = UserDataHideShow.objects.get(id=1)
#             if i.get('name') == 'sr':
#                 data.sr = i.get('checked')
#                 data.save()
#             if i.get('name') == 'name':
#                 data.name = i.get('checked')
#                 data.save()
#             if i.get('name') == 'email':
#                 data.email = i.get('checked')
#                 data.save()
#             if i.get('name') == 'roll':
#                 data.role = i.get('checked')
#                 data.save()
#             if i.get('name') == 'action':
#                 data.action = i.get('checked')
#                 data.save()
#         return JsonResponse({'status':"success","message":"Status Change Succesfully !!!"})

#     return JsonResponse({'status':"success","message":"Status Change Succesfully !!!"})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_superadmin(request):
    if request.method == "POST":
        first_name = request.POST.get("firstname")
        last_name = request.POST.get("lastname")
        email = request.POST.get("email")
        mobile = request.POST.get("contactnumber")
        roll = request.POST.get("superadmin")

        password = generatePassword()
        if User.objects.filter(email=email).exists():

            messages.error(request, "Email already existed.")
            return redirect("add_superadmin")
        if not (
            first_name
            and not first_name.isspace()
            and last_name
            and not last_name.isspace()
            and email
            and not email.isspace()
            and mobile
            and not mobile.isspace()
        ):

            messages.error(request, "Required all fields ")
            return redirect("add_superadmin")
        data = User.objects.create(
            first_name=first_name,
            password=make_password(password),
            last_name=last_name,
            mobile_number=mobile,
            email=email,
            roll=roll,
        )
        data.save()
        subject = "Welcome to   Honest Sherpa world"
        message = f"Hi {first_name}, Thank you for  registering  on Honest Sherpa . Your password is ---  {password}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, "Customer successfully registerted!")
        return redirect("superadmin")
    return render(
        request,
        "admin/UserManagement/superadmin_register.html",
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_superadmin(request, slug):
    try:
        edit_data = User.objects.get(slug=slug)

        if request.method == "POST":
            edit_fisrt_name = request.POST.get("firstname")

            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact = request.POST.get("contactnumber")
            if not (
                edit_fisrt_name
                and not edit_fisrt_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_email
                and not edit_email.isspace()
                and edit_contact
                and not edit_contact.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/edit_superadmin/" + str(slug))

            edit_data.first_name = edit_fisrt_name
            edit_data.last_name = edit_last_name
            edit_data.email = edit_email
            edit_data.mobile_number = edit_contact
            edit_data.save()
            messages.success(request, "Update successfully done!!")
            return redirect("/admin/customer-view/" + str(slug))
    except:
        messages.error(request, "Something went wrong !!")
        return redirect("/admin/edit_superadmin/" + str(slug))

    return render(
        request, "admin/UserManagement/superadmin_edit.html", {"edit_data": edit_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def superadmin_delete(request, id):
    view_detail_data = User.objects.get(id=id)
    view_detail_data.delete()
    messages.error(request, "Delete successfully done!!")
    return redirect("superadmin")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def homeowner(request):
    homeowner = User.objects.filter(roll="homeowner").order_by("-id")
    return render(
        request, "admin/UserManagement/homeowner.html", {"homeowner": homeowner}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_homeowner(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("firstname")
            last_name = request.POST.get("lastname")
            email = request.POST.get("email")
            mobile = request.POST.get("contactnumber")
            roll = request.POST.get("homeowner")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zipcode = request.POST.get("zipcode")
            image = request.FILES.get("image")
            is_active = request.POST.get("status")

            password = generatePassword()
            if User.objects.filter(email=email).exists():

                messages.error(request, "Email already exists.")
                return redirect("add_homeowner")
            if not (
                first_name
                and not first_name.isspace()
                and last_name
                and not last_name.isspace()
                and email
                and not email.isspace()
                and mobile
                and not mobile.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("add_homeowner")

            data = User.objects.create(
                first_name=first_name,
                password=make_password(password),
                last_name=last_name,
                mobile_number=mobile,
                email=email.lower(),
                is_verified=True,
                roll=roll,
                time_zone=timezone,
                identification_number=identification_number,
                manager=manager,
                description=description,
                department=department,
                profile_pic=image,
                fax=fax,
                is_active=is_active,
            )
            data.save()
            address_data = UserMultipleAddress.objects.create(
                city=city,
                country=country,
                address=address,
                zip_code=zipcode,
                state=state,
                user_id=data.id,
            )
            address_data.save()
            subject = " Welcome to   Honest Sherpa world"
            message = f"Hi {first_name}, Thank you for  registering  on Honest Sherpa . Your Email is {email} and Your password is ---  {password}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Homeowner successfully registerted!")
            return redirect("customer_view")
        timeZone = pytz.all_timezones

        return render(
            request,
            "admin/UserManagement/homeowner_register.html",
            {"timeZone": timeZone},
        )

    except:
        messages.error(request, "Something went wrong ")
        return redirect("add_homeowner")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_homeowner(request, slug):
    try:
        edit_data = User.objects.get(slug=slug)
        edit = UserMultipleAddress.objects.filter(user_id=edit_data.id)

        if request.method == "POST":
            edit_first_name = request.POST.get("firstname")

            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact = request.POST.get("contactnumber")
            edit_is_active = request.POST.get("status")
            edit_timezone = request.POST.get("timezone")

            edit_manager = request.POST.get("manager")
            edit_identification_number = request.POST.get("identification_number")
            edit_department = request.POST.get("department")
            edit_description = request.POST.get("description")
            edit_fax = request.POST.get("fax")
            edit_addres = request.POST.get("address")

            edit_country = request.POST.get("country")
            edit_state = request.POST.get("state")
            edit_city = request.POST.get("city")
            edit_zipcode = request.POST.get("zipcode")
            edit_image = request.FILES.get("image")
            if not (
                edit_first_name
                and not edit_first_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_email
                and not edit_email.isspace()
                and edit_contact
                and not edit_contact.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/edit_homeowner/" + str(slug))

            edit_data.first_name = edit_first_name
            edit_data.last_name = edit_last_name
            edit_data.email = edit_email.lower()
            edit_data.mobile_number = edit_contact
            edit_data.is_active = edit_is_active
            edit_data.time_zone = edit_timezone
            edit_data.manager = edit_manager
            edit_data.identification_number = edit_identification_number
            edit_data.department = edit_department
            edit_data.description = edit_description
            edit_data.fax = edit_fax
            if edit_image:
                edit_data.profile_pic = edit_image
            edit_data.save()
            if edit:
                for edit_address in edit:

                    edit_address.address = edit_addres
                    edit_address.country = edit_country
                    edit_address.state = edit_state
                    edit_address.city = edit_city
                    edit_address.zip_code = edit_zipcode
                    edit_address.save()
            else:
                data = UserMultipleAddress.objects.create(
                    address=edit_addres,
                    country=edit_country,
                    state=edit_state,
                    city=edit_city,
                    zip_code=edit_zipcode,
                    user_id=edit_data.id,
                )

            messages.success(request, "Homeowner successfully updated !!")
            return redirect("/admin/details/" + str(slug))
    except:
        messages.error(request, "Something went wrong !!")
        return redirect("/admin/edit_homeowner/" + str(slug))
    timeZone = pytz.all_timezones
    return render(
        request,
        "admin/UserManagement/homeowner_edit.html",
        {"edit_data": edit_data, "edit_address": edit, "timeZone": timeZone},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def homeowner_view_detail(request, slug):
    view_detail_data = User.objects.get(slug=slug)

    return render(
        request,
        "admin/UserManagement/homeowner_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def homeowner_delete(request, id):
    view_detail_data = User.objects.get(id=id)
    view_detail_data.delete()
    messages.error(request, "Homeowner deleted Successfully !!")
    return redirect("customer_view")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def propertymanager(request):
    propertydata = User.objects.filter(roll="propertymanager").order_by("-id")

    return render(
        request,
        "admin/UserManagement/propertymanager.html",
        {"propertydata": propertydata},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_propertymanager(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("firstname")
            last_name = request.POST.get("lastname")
            email = request.POST.get("email")
            roll = request.POST.get("propertymanager")
            contact_number = request.POST.get("contactnumber")
            is_active = request.POST.get("status")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            address = request.POST.get("address")
            country = request.POST.get("country")
            state = request.POST.get("state")
            city = request.POST.get("city")
            zipcode = request.POST.get("zipcode")
            image = request.FILES.get("image")

            password = generatePassword()
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect("add_propertymanager")
            if not (
                first_name
                and not first_name.isspace()
                and last_name
                and not last_name.isspace()
                and email
                and not email.isspace()
                and contact_number
                and not contact_number.isspace()
            ):
                messages.error(request, "Required all fields ")
                return redirect("add_propertymanager")

            registration_data = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email.lower(),
                roll=roll,
                mobile_number=contact_number,
                is_active=is_active,
                is_verified=True,
                time_zone=timezone,
                identification_number=identification_number,
                manager=manager,
                description=description,
                department=department,
                profile_pic=image,
                fax=fax,
                password=make_password(password),
            )
            registration_data.save()
            address_data = UserMultipleAddress.objects.create(
                city=city,
                country=country,
                address=address,
                zip_code=zipcode,
                state=state,
                user_id=registration_data.id,
            )
            address_data.save()
            subject = "Welcome to Honest Sherpa world"
            message = f"Hi {first_name}, Thank you for  registering  on Honest Sherpa .Your Email is {email} and Your password is ---  {password}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)

            messages.success(request, " PropertyOwner  successfully registered !!!")
            return redirect("customer_view")

    except:
        messages.error(request, "Something Went Wrong!")
        return redirect("add_propertymanager")
    timeZone = pytz.all_timezones

    return render(
        request, "admin/UserManagement/propertymanager_add.html", {"timeZone": timeZone}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_propertymanager(request, slug):
    try:
        edit_data = User.objects.get(slug=slug)
        edit = UserMultipleAddress.objects.filter(user_id=edit_data.id)

        if request.method == "POST":
            edit_first_name = request.POST.get("firstname")

            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact = request.POST.get("contactnumber")
            edit_data_is_active = request.POST.get("status")
            edit_timezone = request.POST.get("timezone")

            edit_manager = request.POST.get("manager")
            edit_identification_number = request.POST.get("identification_number")
            edit_department = request.POST.get("department")
            edit_description = request.POST.get("description")
            edit_fax = request.POST.get("fax")
            edit_addres = request.POST.get("address")

            edit_country = request.POST.get("country")
            edit_state = request.POST.get("state")
            edit_city = request.POST.get("city")
            edit_zipcode = request.POST.get("zipcode")
            edit_image = request.FILES.get("image")
            if not (
                edit_first_name
                and not edit_first_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_email
                and not edit_email.isspace()
                and edit_contact
                and not edit_contact.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/customer-view/" + str(slug))

            edit_data.first_name = edit_first_name
            edit_data.last_name = edit_last_name
            edit_data.email = edit_email.lower()
            edit_data.mobile_number = edit_contact
            edit_data.is_active = edit_data_is_active
            edit_data.time_zone = edit_timezone
            edit_data.manager = edit_manager
            edit_data.identification_number = edit_identification_number
            edit_data.department = edit_department
            edit_data.description = edit_description
            edit_data.fax = edit_fax
            if edit_image:
                edit_data.profile_pic = edit_image
            edit_data.save()
            if edit:
                for edit_address in edit:

                    edit_address.address = edit_addres
                    edit_address.country = edit_country
                    edit_address.state = edit_state
                    edit_address.city = edit_city
                    edit_address.zip_code = edit_zipcode
                    edit_address.save()
            else:
                data = UserMultipleAddress.objects.create(
                    address=edit_addres,
                    country=edit_country,
                    state=edit_state,
                    city=edit_city,
                    zip_code=edit_zipcode,
                    user_id=edit_data.id,
                )
            messages.success(request, "PropertyManager updated successfully!!")
            return redirect("/admin/details/" + str(slug))
    except:
        messages.error(request, "Something went wrong !!")
        return redirect("/admin/edit_propertymanager/" + str(slug))
    timeZone = pytz.all_timezones
    return render(
        request,
        "admin/UserManagement/propertymanager_edit.html",
        {"edit_data": edit_data, "edit_address": edit, "timeZone": timeZone},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def propertymanager_view_detail(request, slug):
    view_detail_data = User.objects.get(slug=slug)

    return render(
        request,
        "admin/UserManagement/propertymanager_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def propertymanager_delete(request, id):
    view_detail_data = User.objects.get(id=id)
    view_detail_data.delete()
    messages.error(request, "PropertyManager deleted Successfully !!!")
    return redirect("customer_view")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def franchise(request):
    franchise = User.objects.filter(roll="franchise").order_by("-id")

    return render(
        request, "admin/UserManagement/franchise.html", {"franchise": franchise}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def franchise_verificatoin_admin(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        is_active = request.POST.get("is_approve")
        save_status = User.objects.get(id=user_id)
        save_status.is_verified = is_active
        save_status.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Status Submitted Successfully !!!!",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": "Details Submitted Successfully !!!!",
        },
        status=404,
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def property_manager_verificatoin_admin(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        is_active = request.POST.get("is_approve")
        save_status = User.objects.get(id=user_id)
        save_status.is_active = is_active
        save_status.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Status Submitted Successfully !!!!",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": "Details Submitted Successfully !!!!",
        },
        status=404,
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def vacationer_verificatoin_admin(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        is_active = request.POST.get("is_approve")
        save_status = User.objects.get(id=user_id)
        save_status.is_active = is_active
        save_status.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Status Submitted Successfully !!!!",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": "Details Submitted Successfully !!!!",
        },
        status=404,
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def homeowner_verificatoin_admin(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        is_active = request.POST.get("is_approve")
        save_status = User.objects.get(id=user_id)
        save_status.is_active = is_active
        save_status.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "Status Submitted Successfully !!!!",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": "Details Submitted Successfully !!!!",
        },
        status=404,
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_franchise(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("firstname")
            last_name = request.POST.get("lastname")
            email = request.POST.get("email")
            roll = request.POST.get("franchise")
            contact_number = request.POST.get("contactnumber")
            address = request.POST.get("address")
            country = request.POST.get("country")
            pincode = request.POST.get("pincode[0]name")
            state = request.POST.get("state")
            city = request.POST.get("city")
            license = request.POST.get("license")
            id_number = request.POST.get("id_number")
            company_name = request.POST.get("company_name")
            company_address = request.POST.get("company_address")
            count = request.POST.get("count")
            
            is_active = request.POST.get("is_active")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            image = request.FILES.get("image")

            password = generatePassword()

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already existed.")
                return redirect("add_franchise")

            if not (
                first_name
                and not first_name.isspace()
                and last_name
                and not last_name.isspace()
                and email
                and not email.isspace()
                and contact_number
                and not contact_number.isspace()
            ):
                messages.error(request, "Required all fields ")
                return redirect("add_franchise")
            registration_data = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email.lower(),
                roll=roll,
                mobile_number=contact_number,
                time_zone=timezone,
                identification_number=identification_number,
                manager=manager,
                description=description,
                department=department,
                fax=fax,
                profile_pic=image,
                # zip_code=pincode,
                license_number=license,
                id_number=id_number,
                company_name=company_name,
                company_address=company_address,
                is_active=is_active,
                password=make_password(password),
            )
            registration_data.save()
            address_data = UserMultipleAddress.objects.create(
                city=city,
                country=country,
                address=address,
                zip_code=pincode,
                state=state,
                user_id=registration_data.id,
            )
            address_data.save()
            if not count == "0":
              
               
                for i in range(int(count)):
                    pincode = request.POST.get(f"pincode[{i}]name")
                  
                    FranchisePinCodes.objects.create(
                        pin_code=pincode, user_id=registration_data.id
                    )
            else:
                
                FranchisePinCodes.objects.create(
                    pin_code=pincode, user_id=registration_data.id
                )

            subject = "Welcome to Honest Sherpa world"
            message = f"Hi {first_name}, Thank you for  registering  on Honest Sherpa . Your email is {email} and  Your password is ---  {password}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            Notification.objects.create(
                sender_id=registration_data.id,
                notification_type="created",
                notification=f"{registration_data.first_name} is successfully created.",
            )
            messages.success(request, "successfully registerted!")
            return redirect("customer_view")

    except:
        messages.error(request, "Something Went Wrong!")
        return redirect("add_franchise")

    timeZone = pytz.all_timezones
    return render(
        request, "admin/UserManagement/franchise_add.html", {"timeZone": timeZone}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_franchise(request, slug):
    try:
        edit_data = User.objects.get(slug=slug)

        edit = UserMultipleAddress.objects.filter(user_id=edit_data.id)

        if request.method == "POST":
            edit_fisrt_name = request.POST.get("firstname")
            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact = request.POST.get("contactnumber")
            edit_addres = request.POST.get("address")
            edit_country = request.POST.get("country")
            edit_state = request.POST.get("state")
            edit_city = request.POST.get("city")
            edit_pincode = request.POST.get("pincode")
            edit_license = request.POST.get("license")
            edit_id_number = request.POST.get("id_number")
            edit_company_name = request.POST.get("company_name")
            edit_company_address = request.POST.get("company_address")
            edit_is_active = request.POST.get("is_active")
            count = request.POST.get("pincode_count")
            timezone = request.POST.get("timezone")

            manager = request.POST.get("manager")
            identification_number = request.POST.get("identification_number")
            department = request.POST.get("department")
            description = request.POST.get("description")
            fax = request.POST.get("fax")
            image = request.FILES.get("image")

            del_data = FranchisePinCodes.objects.filter(user_id=edit_data.id).delete()
            if not (
                edit_fisrt_name
                and not edit_fisrt_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_email
                and not edit_email.isspace()
                and edit_contact
                and not edit_contact.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/edit_franchise/" + str(slug))

            edit_data.first_name = edit_fisrt_name
            edit_data.last_name = edit_last_name
            edit_data.email = edit_email.lower()
            edit_data.mobile_number = edit_contact

            edit_data.license_number = edit_license
            edit_data.id_number = edit_id_number
            edit_data.company_name = edit_company_name
            edit_data.company_address = edit_company_address
            edit_data.is_active = edit_is_active
            edit_data.time_zone = timezone
            edit_data.manager = manager
            edit_data.identification_number = identification_number
            edit_data.department = department
            edit_data.description = description
            edit_data.fax = fax
            if image:
                edit_data.profile_pic = image

            edit_data.save()
            for edit_address in edit:

                edit_address.country = edit_country
                edit_address.state = edit_state
                edit_address.city = edit_city
                if edit_pincode:
                    edit_address.zip_code = edit_pincode
                edit_address.address = edit_addres
                edit_address.save()

            messages.success(request, "Update successfully done!!")
            if count:
                for i in range(int(count)):
                    pin_code = request.POST.get(f"pincode[{i}]name")
                    FranchisePinCodes.objects.create(
                        user_id=edit_data.id,
                        pin_code=pin_code,
                    )
                return redirect("/admin/details/" + str(slug))

        pincodes_count = FranchisePinCodes.objects.filter(user_id=edit_data.id).count()
        pincodes = FranchisePinCodes.objects.filter(user_id=edit_data.id)
        timeZone = pytz.all_timezones
        return render(
            request,
            "admin/UserManagement/franchise_edit.html",
            {
                "edit_data": edit_data,
                "pincodes_count": pincodes_count,
                "pincodes": pincodes,
                "edit_address": edit,
                "timeZone": timeZone,
            },
        )
    except:
        messages.error(request, "Something went wrong !!")
        return redirect("/admin/edit_franchise/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def franchise_view_detail(request, slug):
    view_detail_data = User.objects.get(slug=slug)

    return render(
        request,
        "admin/UserManagement/franchise_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def franchise_delete(request, id):
    view_detail_data = User.objects.get(id=id)
    view_detail_data.delete()
    messages.error(request, "Delete successfully done!!")
    return redirect("franchise")


# Global Setting CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def globalsetting(request):
    global_data = GlobalSetting.objects.all().order_by("-id")
    return render(
        request, "admin/globalsetting/globalsetting.html", {"global_data": global_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def globalsetting_add(request):
    try:
        if request.method == "POST":
            text = request.POST.get("title")
            image = request.FILES.get("image")

            insta_url = request.POST.get("insta_url")
            facebook_url = request.POST.get("facebook_url")
            twitter_url = request.POST.get("twitter_url")

            status = request.POST.get("status")
            if not (
                text
                and not text.isspace()
                and image
                and insta_url
                and not insta_url.isspace()
                and facebook_url
                and not facebook_url.isspace()
                and twitter_url
                and not twitter_url.isspace()
                and status
                and not status.isspace()
            ):
                messages.error(request, "Required all fields ")
                return redirect("globalsetting_add")

            setting_global = GlobalSetting.objects.create(
                title=text,
                global_image=image,
                global_url_insta=insta_url,
                global_url_facebook=facebook_url,
                global_url_twitter=twitter_url,
                is_active=status,
            )
            setting_global.save()

            messages.success(request, "Social Account Add Successfully !!")
            return redirect("globalsetting")
    except:
        messages.success(request, "Smething went wrong !!")
        return redirect("globalsetting_add")
    return render(request, "admin/globalsetting/globalsetting_add.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def globalsetting_edit(request, slug):
    edit_data = GlobalSetting.objects.get(slug=slug)
    try:
        if request.method == "POST":
            edit_title = request.POST.get("title")
            edit_image = request.FILES.get("image")

            insta_url = request.POST.get("insta_url")
            facebook_url = request.POST.get("facebook_url")
            twitter_url = request.POST.get("twitter_url")
            edit_status = request.POST.get("status")
            if not (
                edit_title
                and not edit_title.isspace()
                and insta_url
                and not insta_url.isspace()
                and facebook_url
                and not facebook_url.isspace()
                and twitter_url
                and not twitter_url.isspace()
                and edit_status
                and not edit_status.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/globalsetting_edit/" + str(slug))

            if edit_image:
                edit_data.global_image = edit_image

            edit_data.text = edit_title
            # edit_data.global_image=edit_image
            edit_data.global_url_insta = insta_url
            edit_data.global_url_facebook = facebook_url
            edit_data.global_url_twitter = twitter_url
            edit_data.is_active = edit_status

            edit_data.save()
            messages.success(request, "GlobalSetting updated successfully!!!")
            return redirect("globalsetting")

    except:

        messages.error(request, "Something Went Wrong!!!")
        return redirect("/admin/globalsetting_edit/" + str(slug))

    return render(
        request, "admin/globalsetting/globalsetting_edit.html", {"edit_data": edit_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def globalsetting_view_detail(request, slug):
    view_detail_data = GlobalSetting.objects.get(slug=slug)
    return render(
        request,
        "admin/globalsetting/globalsetting_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def globalsetting_delete(request, id):
    data = GlobalSetting.objects.get(id=id)
    data.delete()
    messages.error(request, "Deleted Successfully!!")
    return redirect("globalsetting")


# Testimonial CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def testimonial(request):
    testimonial_data = Testimonial.objects.all().order_by("-id")
    return render(
        request,
        "admin/testimonial/testimonial.html",
        {"testimonial_data": testimonial_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def testimonial_add(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")

            image = request.FILES.get("image")

            desgination = request.POST.get("desgination")

            description = request.POST.get("descrip")

            status = request.POST.get("status")

            if not (
                name
                and not name.isspace()
                and image
                and desgination
                and not desgination.isspace()
                and description
                and not description.isspace()
                and status
                and not status.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("testimonial")

            testimonial = Testimonial.objects.create(
                name=name,
                testimonial_image=image,
                desgination=desgination,
                description=description,
                is_active=status,
            )

            testimonial.save()
            messages.success(request, "Testimonial Added Successfully Done!!!")
            return redirect("testimonial")
    except:
        messages.error(request, "Something Went Wrong")
        return redirect("testimonial_add")

    return render(request, "admin/testimonial/testimonial_add.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def testimonial_edit(request, slug):
    edit_data = Testimonial.objects.get(slug=slug)
    try:
        if request.method == "POST":
            edit_name = request.POST.get("name")
            edit_image = request.FILES.get("image")
            edit_desgination = request.POST.get("desgination")
            edit_description = request.POST.get("descrip")
            edit_status = request.POST.get("status")
            if not (
                edit_name
                and not edit_name.isspace()
                and edit_desgination
                and not edit_desgination.isspace()
                and edit_description
                and not edit_description.isspace()
                and edit_status
                and not edit_status.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/testimonial")
            if edit_image:
                edit_data.testimonial_image = edit_image
            edit_data.name = edit_name
            # edit_data.testimonial_image=edit_image
            edit_data.desgination = edit_desgination
            edit_data.description = edit_description
            edit_data.is_active = edit_status
            edit_data.save()
            messages.success(request, "Update Successfully Done!!!")
            return redirect("/admin/testimonial")
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/testimonial_edit/" + str(slug))

    return render(
        request, "admin/testimonial/testimonial_edit.html", {"edit_data": edit_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def testimonial_view_detail(request, slug):
    view_detail_data = Testimonial.objects.get(slug=slug)
    return render(
        request,
        "admin/testimonial/testimonial_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def testimonial_delete(request, id):
    data = Testimonial.objects.get(id=id)
    data.delete()
    messages.error(request, "Delete successfully done!!")
    return redirect("testimonial")


# Email Template CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def emailtemplate(request):
    email_data = EmailTemplate.objects.all().order_by("-id")
    return render(
        request, "admin/email_template/emailtemplate.html", {"email_data": email_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def emailtemplate_add(request):
    try:
        if request.method == "POST":
            title = request.POST.get("title")

            content = request.POST.get("content")

            status = request.POST.get("status")

            if not (
                title
                and not title.isspace()
                and content
                and not content.isspace()
                and status
                and not status.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("emailtemplate_add")

            emailtemplate = EmailTemplate.objects.create(
                title=title, content=content, is_active=status
            )

            emailtemplate.save()
            messages.success(request, "Email Template Added Successfully Done!!!")
            return redirect("emailtemplate")
    except:
        messages.error(request, "Something Went Wrong")
        return redirect("emailtemplate_add")

    return render(request, "admin/email_template/emailtemplate_add.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def emailtemplate_edit(request, slug):
    edit_data = EmailTemplate.objects.get(slug=slug)
    try:
        if request.method == "POST":
            edit_title = request.POST.get("title")

            edit_content = request.POST.get("content")

            edit_status = request.POST.get("status")
            if not (
                edit_title
                and not edit_title.isspace()
                and edit_content
                and not edit_content.isspace()
                and edit_status
                and not edit_status.isspace()
            ):

                messages.error(request, "Required all fields ")
                return redirect("/admin/emailtemplate_edit/" + str(slug))

            edit_data.title = edit_title

            edit_data.content = edit_content

            edit_data.is_active = edit_status
            edit_data.save()
            messages.success(request, "Email Template  Update Successfully !!!")
            return redirect("emailtemplate")
    except:
        messages.error(request, "Something Went Wrong!!!")
        return redirect("/admin/emailtemplate_edit/" + str(slug))

    return render(
        request,
        "admin/email_template/emailtemplate_edit.html",
        {"edit_data": edit_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def emailtemplate_view_detail(request, slug):
    view_detail_data = EmailTemplate.objects.get(slug=slug)
    return render(
        request,
        "admin/email_template/emailtemplate_view_detail.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def emailtemplate_delete(request, id):
    data = EmailTemplate.objects.get(id=id)
    data.delete()
    messages.error(request, "Email Template  Delete successfully !!")
    return redirect("emailtemplate")


# Contact Us:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def pending_list(request):
    list_data = Contact.objects.all().order_by("-id")
    return render(
        request, "admin/contactus/pending_list.html", {"list_data": list_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def pending_list_add(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            question = request.POST.get("question")
            status = request.POST.get("status")
            if not (
                email
                and not email.isspace()
                and question
                and not question.isspace()
                and status
                and not status.isspace()
            ):
                messages.error(request, "All Fields Are Required")
                return redirect("pending_list_add")

            add_data = Contactus.objects.create(
                email=email, question=question, is_pending=status
            )
            add_data.save()
            messages.success(request, "list Add successfully done!!")
            return redirect("pending_list_add")
    except:
        messages.error(request, "Something Went Wrong")
        return redirect("pending_list_add")

    return render(request, "admin/contactus/pending_list_add.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def pending_list_reply(request, slug):
    reply_list = Contact.objects.get(slug=slug)
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            if not (answer and not answer.isspace()):
                messages.error(request, "Answer field required")
                return redirect("/admin/pending_list_reply/" + str(slug))
            reply_list.question = question
            reply_list.answer = answer

            reply_list.save()
            subject = f"{question}"
            message = f"Hi  Here is your answer is:{answer}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            mail_send = send_mail(subject, message, email_from, recipient_list)

            if mail_send == 1:  # pending list to resolve list
                reply_list.is_pending = False
                reply_list.answer = answer
                reply_list.replied_time = datetime.datetime.now()
                reply_list.save()

            else:
                messages.error(request, "Mail not send")
            messages.success(request, "Email Send Successfully")
            return redirect("pending_list")
    except:
        messages.error(request, "Something Went Wrong!!!")
        return redirect("/admin/pending_list_reply/" + str(slug))

    return render(
        request, "admin/contactus/pending_list_reply.html", {"reply_list": reply_list}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def reslove_list(request):
    reslove_list_data = Contactus.objects.filter(is_pending=False).order_by("-id")
    return render(
        request,
        "admin/contactus/reslove_list.html",
        {"reslove_list_data": reslove_list_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def reslove_list_delete(request, id):
    data = Contactus.objects.get(id=id)
    data.delete()
    messages.error(request, "Delete Succcessfully Done!!!")
    return redirect("reslove_list")


# Admin Profile :


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_profile(request, slug):
    view_profile_data = User.objects.get(slug=slug)
    try:
        if request.method == "POST":
            edit_first_name = request.POST.get("firstname")
            edit_last_name = request.POST.get("lastname")
            edit_email = request.POST.get("email")
            edit_contact_number = request.POST.get("contactnumber")
            image = request.FILES.get("image")

            if not (
                edit_first_name
                and not edit_first_name.isspace()
                and edit_last_name
                and not edit_last_name.isspace()
                and edit_contact_number
                and not edit_contact_number.isspace()
            ):
                messages.error(request, "All Fields Are Required")
                return redirect("/admin/view-profile/" + str(slug))
            if image:
                view_profile_data.first_name = edit_first_name
                view_profile_data.last_name = edit_last_name
                view_profile_data.mobile_number = edit_contact_number
                view_profile_data.profile_pic = image
                view_profile_data.save()
            else:
                view_profile_data.first_name = edit_first_name
                view_profile_data.last_name = edit_last_name
                view_profile_data.mobile_number = edit_contact_number
                view_profile_data.save()
            messages.success(request, "Update Successfully Done!!")
            return redirect("/admin/view-profile/" + str(slug))

    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/view-profile/" + str(slug))
    return render(
        request,
        "admin/admin_profile/view_profile.html",
        {"view_profile_data": view_profile_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def change_password(request, slug):
    user = User.objects.get(slug=slug)
    try:
        if request.method == "POST":
            old_password = request.POST.get("oldPassword")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if old_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/admin/change-password/" + str(slug))
            if new_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/admin/change-password/" + str(slug))
            if confirm_password.isspace():
                messages.error(request, "Please enter valid password!")
                return redirect("/admin/change-password/" + str(slug))
            if check_password(old_password, user.password):
                if new_password != confirm_password:
                    messages.error(request, "Password does not matched")
                    return redirect("/admin/change-password/" + str(slug))
                user.set_password(confirm_password)
                user.save()
                auth.login(request, user)
                messages.success(request, "Password successfully changed!")
                return redirect("/admin/view-profile/" + str(slug))
            else:
                messages.error(request, "Password does not matched")
                return redirect("/admin/change-password/" + str(slug))

    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/change-password/" + str(slug))

    return render(
        request,
        "admin/admin_profile/user_changepassword.html",
        {"change_password_data": user},
    )


# Product Mangement CURD :
# 1. Category Mangement:
@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def category(request):

    category = ProductCategory.objects.all().order_by("id")
    return render(
        request, "admin/ProductManagement/category.html", {"category": category}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        status = request.POST.get("status")
        if ProductCategory.objects.filter(name=name).exists():
            messages.error(request, "Category Already Exits")
            return redirect("/admin/add-category/")
        else:
            ProductCategory.objects.create(
                name=name, category_image=image, is_active=status
            )

            messages.success(request, "Category created successfully.")
            return redirect("/admin/category/")
    return render(request, "admin/ProductManagement/add_category.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_category(request, slug):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")

        status = request.POST.get("status")

        if image:
            data = ProductCategory.objects.get(slug=slug)
            data.name = name
            data.category_image = image
            data.is_active = status
            data.save()
            messages.success(request, "Category Update successfully")
            return redirect("/admin/category/")
        else:
            data = ProductCategory.objects.get(slug=slug)
            data.name = name
            data.is_active = status
            data.save()
            messages.success(request, "Category Update successfully")
            return redirect("/admin/category/")
    category = ProductCategory.objects.get(slug=slug)
    return render(
        request, "admin/ProductManagement/edit_category.html", {"category": category}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_category(request, id):
    category = ProductCategory.objects.get(id=id)
    category.delete()
    return redirect("/admin/category/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_category(request, slug):
    category = ProductCategory.objects.get(slug=slug)
    return render(
        request, "admin/ProductManagement/view_category.html", {"category": category}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def subcategory(request):
    subcategory = ProductSubCategory.objects.all().order_by("id")
    return render(
        request,
        "admin/ProductManagement/subcategory.html",
        {"subcategory": subcategory},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_subcategory(request):
    if request.method == "POST":
        category = request.POST.get("category")
        name = request.POST.get("name")
        image = request.FILES.get("image")
        status = request.POST.get("status")
        data = ProductSubCategory.objects.create(
            category_id=category, name=name, subcategory_image=image, is_active=status
        )
        messages.success(request, "SubCategory add successfully")
        return redirect("/admin/add-subcategory/")
    category = ProductCategory.objects.all()
    return render(
        request, "admin/ProductManagement/add_subcategory.html", {"category": category}
    )


# 2. Product :
@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def product(request):
    product = Product.objects.all().order_by("id")
    product_sku_code = ProductSkuCodes.objects.filter(product_id__in=product)
    return render(
        request,
        "admin/ProductManagement/product.html",
        {"product": product, "product_sku_code": product_sku_code,},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_product(request):
    # try:
    if request.method == "POST":
        category = request.POST.get("category")
        subcategory = request.POST.get("subcategory")
        name = request.POST.get("name")
        # onedayprice = request.POST.get("onedayprice")
        # weekprice = request.POST.get("weekprice")
        # monthprice = request.POST.get("monthprice")
        sale_price = request.POST.get("sale_price")
        # annualprice = (
        #     request.POST.get("annualprice") if request.POST.get("annualprice") else 0
        # )
        # skucode = request.POST.get("skucode")
        feature = request.POST.get("feature")
        product_quantity = request.POST.get("quantity")
        image = request.FILES.get("image")
        image1 = request.FILES.get("image1")
        image2 = request.FILES.get("image2")
        image3 = request.FILES.get("image3")
        image4 = request.FILES.get("image4")
        description = request.POST.get("content")
        # address = request.POST.get("autocom")
        latitude = request.POST.get("lat")
        longitude = request.POST.get("long")
        available = request.POST.get("available")
        franchise = request.POST.getlist("franchise-user[]")
      
        
        purchased_date=request.POST.get('date')
        purchased_price=request.POST.get('purchased_price')
        is_return=request.POST.get('return')       
        status = request.POST.get("status")
        # count = request.POST.get("count")
        # option = request.POST.get("option[0]name")

        # option_image = request.FILES.get("option[0]image")
        # option_key = request.POST.get("option[0]key")
        # option_value = request.POST.get("option[0]value")
        # price = request.POST.get("option[0]price")
        # quantity = request.POST.get("option[0]quantity")
        # price_count = request.POST.get("price_count")

        user_id = request.POST.get("user_id")
        
        vacationer = request.POST.get("vacationer")

        homeowner = request.POST.get("homeowner")
        propertymanager = request.POST.get("propertymanager")

        vacationer_0_7_days = request.POST.get("vacationer_0_7_days")
        vacationer_greaterthan_7_days = request.POST.get(
            "vacationer_greaterthan_7_days"
        )
        homeowner_0_7_days = request.POST.get("homeowner_0_7_days")

        homeowner_greaterthan_7_days = request.POST.get("homeowner_greaterthan_7_days")

        # homeowner_0_7_days_wholesale=request.POST.get('homeowner_0_7_days_wholesale')

        # homeowner_greaterthan_7_days_wholesale=request.POST.get('homeowner_greaterthan_7_days_wholesale')

        # propertymanager_0_7_days=request.POST.get('propertymanager_0_7_days')

        # propertymanager_greaterthan_7_days=request.POST.get('propertymanager_greaterthan_7_days')

        propertymanager_0_7_days_wholesale = request.POST.get(
            "propertymanager_0_7_days_wholesale"
        )

        propertymanager_greaterthan_7_days_wholesale = request.POST.get(
            "propertymanager_greaterthan_7_days_wholesale"
        )

        user_ids = eval(user_id)
       
       
      

        if subcategory:

            data = Product.objects.create(
                category_id=category,
                subcategory_id=subcategory,
                quantity=product_quantity,
                name=name,
                # option_id=option,
                description=description,
                avaliable=available,
                is_return=is_return,
                is_active=status,
                
                is_feature=feature,
                image=image,
                image1=image1,
                image2=image2,
                image3=image3,
                image4=image4,
              
                latitude=latitude,
                longitude=longitude,
                purchased_date=purchased_date,
                purchased_price=purchased_price
            )
        else:
            data = Product.objects.create(
                category_id=category,
                subcategory_id="",
                quantity=product_quantity,
                name=name,
                # option_id=option,
                description=description,
                avaliable=available,
                is_return=is_return,
                is_active=status,
              
                is_feature=feature,
                image=image,
                image1=image1,
                image2=image2,
                image3=image3,
                image4=image4,
                
                latitude=latitude,
                longitude=longitude,
                purchased_date=purchased_date,
                purchased_price=purchased_price
            )

        # if count:
        #     for i in range(int(count)):
        #         options = request.POST.get(f"option[{i}]name")
        #         option_images = request.FILES.get(f"option[{i}]image")
        #         option_keys = request.POST.get(f"option[{i}]key")
        #         option_values = request.POST.get(f"option[{i}]value")
        #         prices = request.POST.get(f"option[{i}]price")
        #         quantities = request.POST.get(f"option[{i}]quantity")
        #         option_data = ProductOptions.objects.create(
        #             product_id=data.id,
        #             option_id=options,
        #             option_value_id=option_keys,
        #             price=prices,
        #             quantity=quantities,
        #             Productoptions_image=option_images,
        #         )
        # else:
        #     option_data = ProductOptions.objects.create(
        #         product_id=data.id,
        #         option_id=option,
        #         option_value_id=option_key,
        #         price=price,
        #         quantity=quantity,
        #         Productoptions_image=option_image,
        # )
        franchise_user_list=[]
        for fran in franchise:
            franchise_data=ProductFranchiseMember.objects.create(user_id=fran,product_id=data.id)
            franchise_user_list.append(franchise_data.user_id)
        pincode = FranchisePinCodes.objects.filter(user_id__in=franchise_user_list)
    
        if is_return == "True":
            for i in pincode:
                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    product_id=data.id,
                    user_type="vacationer",
                    zero_seven_days=vacationer_0_7_days,
                    greaterthan_seven=vacationer_greaterthan_7_days,
                    user_id=i.user_id,
                )

                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    user_type="homeowner",
                    zero_seven_days=homeowner_0_7_days,
                    product_id=data.id,
                    greaterthan_seven=homeowner_greaterthan_7_days,
                    user_id=i.user_id,
                )

                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    user_type="propertymanager",
                    zero_seven_days_wholesale=propertymanager_0_7_days_wholesale,
                    product_id=data.id,
                    greaterthan_seven_wholesale=propertymanager_greaterthan_7_days_wholesale,
                    user_id=i.user_id,
                )
            FranchisePrice.objects.create(product_id=data.id,user_type="vacationer",zero_seven_days=vacationer_0_7_days,
            greaterthan_seven=vacationer_greaterthan_7_days)
            FranchisePrice.objects.create(product_id=data.id, user_type="homeowner", zero_seven_days=homeowner_0_7_days,
            greaterthan_seven=homeowner_greaterthan_7_days,)
            FranchisePrice.objects.create(product_id=data.id,user_type="propertymanager",zero_seven_days_wholesale=propertymanager_0_7_days_wholesale,
            greaterthan_seven_wholesale=propertymanager_greaterthan_7_days_wholesale)        
        else:
            for i in pincode:
                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    product_id=data.id,
                    user_type="vacationer",
                    sale_price=sale_price,
                    user_id=i.user_id,
                )

                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    user_type="homeowner",
                    sale_price=sale_price,
                    product_id=data.id,
                   
                    user_id=i.user_id,
                )

                FranchisePinCodesPrice.objects.create(
                    pin_code=i.pin_code,
                    user_type="propertymanager",
                    sale_price=sale_price,
                    product_id=data.id,
                    
                    user_id=i.user_id,
                )
            FranchisePrice.objects.create(product_id=data.id,user_type="vacationer",sale_price=sale_price)
            FranchisePrice.objects.create(user_type="homeowner",sale_price=sale_price,product_id=data.id)
            FranchisePrice.objects.create(user_type="propertymanager",sale_price=sale_price,product_id=data.id)
        # # if price_count:
        #     user_types = ["homeowner", "vacationer", "propertymanager"]
        #     for u in user_types:

        #         for i in range(1, int(price_count)):
        #             user = request.POST.get(f"user[{u}][{i}]user")

        #             user_type = request.POST.get(f"user_type[{u}][{i}]user_type")

        #             pincodes = request.POST.get(f"pincodes[{u}][{i}]pincode")

        #             daily = request.POST.get(f"daily[{u}][{i}]daily")

        #             weekly = request.POST.get(f"weekly[{u}][{i}]weekly")

        #             # yearly = request.POST.get(f"yearly[{u}][{i}]yearly")

        #             # twoweekly = request.POST.get(f"twoweekly[{u}][{i}]twoweekly")

        #             # monthly = request.POST.get(f"monthly[{u}][{i}]monthly")

        #             dailywholesale = request.POST.get(
        #                 f"dailywholesale[{u}][{i}]dailywholesale"
        #             )

        #             weeklywholesale = request.POST.get(
        #                 f"weeklywholesale[{u}][{i}]weeklywholesale"
        #             )

        #             # twoweeklywholesale = request.POST.get(
        #             #     f"twoweeklywholesale[{u}][{i}]twoweeklywholesale"
        #             # )

        #             # monthlywholesale = request.POST.get(
        #             #     f"monthlywholesale[{u}][{i}]monthlywholesale"
        #             # )

        #             # yearlywholesale = request.POST.get(
        #             #     f"yearlywholesale[{u}][{i}]yearlywholesale"
        #             # )

        #             price_data = FranchisePinCodesPrice.objects.create(
        #                 product_id=data.id,
        #                 pin_code=pincodes,
        #                 daily_price=daily,
        #                 weekly_price=weekly,
        #                 # yearly_price=yearly,
        #                 # two_weekly_price=twoweekly,
        #                 # monthly_price=monthly,
        #                 daily_wholesale_price=dailywholesale,
        #                 weekly_wholesale_price=weeklywholesale,
        #                 # twoweekly_wholesale_price=twoweeklywholesale,
        #                 # monthly_wholesale_price=monthlywholesale,
        #                 # yearly_wholesale_price=yearlywholesale,
        #                 user_id=user,
        #                 user_type=user_type,
        #             )
        if product_quantity:

            cat_id = ProductCategory.objects.get(id=category)
            SKU_CODE = cat_id.name.upper()[0:2] + name.upper()[0:3] + "00"
            digits = 1
            sku_code = SKU_CODE
            all_product = ProductSkuCodes.objects.all()
            skuList = []
            for i in all_product:
                spilts = i.sku_code
                Str = spilts[:-1]
                if sku_code == Str:

                    skuList.append(Str)
            count = len(skuList)
            for j in range(0, int(product_quantity)):
                if ProductSkuCodes.objects.filter(sku_code=sku_code + str(digits)):
                    ProductSkuCodes.objects.create(
                        product_id=data.id, sku_code=sku_code + str(int(count + 1))
                    )
                    count += 1
                else:
                    ProductSkuCodes.objects.create(
                        product_id=data.id, sku_code=sku_code + str(digits)
                    )

                    digits += 1
        messages.success(request, "Product create successfully !!!!")
        return redirect("/admin/product/")
    category = ProductCategory.objects.all()
    subcategory = ProductSubCategory.objects.all()
    # option = Options.objects.all()
    user = User.objects.filter(roll="franchise")

    propertymanager = User.objects.filter(propertymanager_negotiable="1")

    return render(
        request,
        "admin/ProductManagement/add_product.html",
        {
            "category": category,
            # "option": option,
            "subcategory": subcategory,
            "franchise_user": user,
            "propertymanager": propertymanager,
        },
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def product_ajax(request):
    if request.method == "POST":
        user_ids = request.POST.getlist("info_user[]")
        input_count = int(request.POST.get("input_count"))

        user_type = request.POST.get("user_type")

        get_pincode = FranchisePinCodes.objects.filter(user_id__in=user_ids)

        j = input_count
        for i in get_pincode:
            j = j + 1
            i.pincode_index = j
            i.user_type = user_type
        return render(
            request,
            "admin/ProductManagement/vacationer_product_pincode.html",
            {"user": get_pincode},
        )
    return JsonResponse({"status": "error"})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def test(request):
    return render(request, "admin/ProductManagement/product_pincode.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def select_subcategory(request):
    if request.method == "POST":
        try:
            category_id = request.POST.get("category_id")
            data = ProductSubCategory.objects.filter(category_id=category_id).values()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Details Submitted Successfully !!!!",
                    "data": list(data),
                },
                status=200,
            )
        except:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Something went wrong",
                },
                status=404,
            )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_product(request, slug):
    try:
        template_name="admin/ProductManagement/edit_product.html"
        product = Product.objects.get(slug=slug)
        franchiseuser=ProductFranchiseMember.objects.filter(product_id=product.id).values_list('user_id', flat=True)
        franchise_price=FranchisePrice.objects.filter(product_id=product.id)
        if request.method == "POST":
            category = request.POST.get("category")
            subcategorys = request.POST.get("subcategory")
            name = request.POST.get("name")
            sale_price = request.POST.get("sale_price")
            feature = request.POST.get("feature")
            product_quantity = request.POST.get("quantity")
            image = request.FILES.get("image0")
            image1 = request.FILES.get("image1")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")
            image4 = request.FILES.get("image4")
            description = request.POST.get("content")
            available = request.POST.get("available")
            franchises = request.POST.getlist("franchise-user[]")
            purchased_date=request.POST.get('date')
            purchased_price=request.POST.get('purchased_price')
            is_return=request.POST.get('return')       
            status = request.POST.get("status")
            user_id = request.POST.get("user_id")
            vacationer = request.POST.get("vacationer")
            homeowner = request.POST.get("homeowner")
            propertymanager = request.POST.get("propertymanager")
            vacationer_0_7_days = request.POST.get("vacationer_0_7_days")
            vacationer_greaterthan_7_days = request.POST.get(
                "vacationer_greaterthan_7_days"
            )
            homeowner_0_7_days = request.POST.get("homeowner_0_7_days")
            homeowner_greaterthan_7_days = request.POST.get("homeowner_greaterthan_7_days")
            propertymanager_0_7_days_wholesale = request.POST.get(
                "propertymanager_0_7_days_wholesale"
            )
            propertymanager_greaterthan_7_days_wholesale = request.POST.get(
                "propertymanager_greaterthan_7_days_wholesale"
            )
            if subcategorys:
                product.category_id=category
                product.subcategory_id=subcategorys
                product.quantity=product_quantity
                product.name=name
                product.description=description
                product.avaliable=available
                product.is_return=is_return
                product.is_active=status
                product.is_feature=feature
                if image :
                    product.image=image
                if image1:
                    product.image1=image1
                if image2:
                    product.image2=image2
                if image3:
                    product.image3=image3
                if image4:
                    product.image4=image4

                product.purchased_date=purchased_date
                product.purchased_price=purchased_price
               
                product.save()
               
            else:
                product.category_id=category
                product.subcategory_id=""
                product.quantity=product_quantity
                product.name=name
                product.description=description
                product.avaliable=available
                product.is_return=is_return
                product.is_active=status
                product.is_feature=feature
                if image :
                    product.image=image
                if image1:
                    product.image1=image1
                if image2:
                    product.image2=image2
                if image3:
                    product.image3=image3
                if image4:
                    product.image4=image4

                product.purchased_date=purchased_date
                product.purchased_price=purchased_price
             
                product.save()
            franchise_remove=ProductFranchiseMember.objects.filter(product_id=product.id).exclude( user_id__in=franchises)
            franchise_remove.delete() 
            franchise_price_remove=FranchisePinCodesPrice.objects.filter(product_id=product.id).exclude( user_id__in=franchises)
            franchise_price_remove.delete()
            franchise_user_list=[]    
            for fran in franchises:
                if not ProductFranchiseMember.objects.filter(product_id=product.id, user_id=fran).exists():
                    franchise_data=ProductFranchiseMember.objects.create(user_id=fran, product_id=product.id)
                    franchise_user_list.append(franchise_data.user_id)
           
            pincode=FranchisePinCodes.objects.filter(user_id__in=franchises) 
            if is_return == "True":
                for i in pincode:
                    if FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id).exists():
                        price=FranchisePinCodesPrice.objects.filter(product_id=product.id, user_type="vacationer", user_id=i.user_id, pin_code=i.pin_code).update(zero_seven_days=vacationer_0_7_days,greaterthan_seven=vacationer_greaterthan_7_days)
                        price=FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id, pin_code=i.pin_code, user_type="homeowner").update(zero_seven_days=homeowner_0_7_days,greaterthan_seven=homeowner_greaterthan_7_days)
                        price=FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id, pin_code=i.pin_code, user_type="propertymanager").update(zero_seven_days_wholesale=propertymanager_0_7_days_wholesale,
                        greaterthan_seven_wholesale=propertymanager_greaterthan_7_days_wholesale)
                        price=FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id, pin_code=i.pin_code).update(sale_price="")

                    else:
                        price=FranchisePinCodesPrice.objects.create(pin_code=i.pin_code,product_id=product.id,user_type="vacationer",
                        zero_seven_days=vacationer_0_7_days, greaterthan_seven=vacationer_greaterthan_7_days, user_id=i.user_id)
                        FranchisePinCodesPrice.objects.create(pin_code=i.pin_code, user_type="homeowner",
                        zero_seven_days=homeowner_0_7_days, product_id=product.id, greaterthan_seven=homeowner_greaterthan_7_days,
                        user_id=i.user_id)
                        FranchisePinCodesPrice.objects.create(pin_code=i.pin_code, user_type="propertymanager", zero_seven_days_wholesale=propertymanager_0_7_days_wholesale, product_id=product.id,greaterthan_seven_wholesale=propertymanager_greaterthan_7_days_wholesale, user_id=i.user_id)
                FranchisePrice.objects.filter(product_id=product.id,user_type="vacationer").update(zero_seven_days=vacationer_0_7_days, greaterthan_seven=vacationer_greaterthan_7_days)
                FranchisePrice.objects.filter(product_id=product.id, user_type="homeowner").update(zero_seven_days=homeowner_0_7_days, greaterthan_seven=homeowner_greaterthan_7_days,)
                FranchisePrice.objects.filter(product_id=product.id,user_type="propertymanager").update(zero_seven_days_wholesale=propertymanager_0_7_days_wholesale,greaterthan_seven_wholesale=propertymanager_greaterthan_7_days_wholesale)
                FranchisePrice.objects.filter(product_id=product.id).update(sale_price="")
            else:
                for i in pincode:
                    if FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id).exists():
                        FranchisePinCodesPrice.objects.filter(pin_code=i.pin_code, product_id=product.id, user_type="vacationer", user_id=i.user_id).update(sale_price=sale_price)
                        FranchisePinCodesPrice.objects.filter(pin_code=i.pin_code, user_type="homeowner",product_id=product.id, user_id=i.user_id).update(sale_price=sale_price)
                        FranchisePinCodesPrice.objects.filter(pin_code=i.pin_code, user_type="propertymanager", product_id=product.id, user_id=i.user_id).update(sale_price=sale_price)
                        price=FranchisePinCodesPrice.objects.filter(product_id=product.id, user_id=i.user_id, pin_code=i.pin_code).update(zero_seven_days="", greaterthan_seven="", zero_seven_days_wholesale="", greaterthan_seven_wholesale="")
                    else:
                        FranchisePinCodesPrice.objects.create(pin_code=i.pin_code, product_id=product.id, user_type="vacationer",sale_price=sale_price, user_id=i.user_id)
                        FranchisePinCodesPrice.objects.create(pin_code=i.pin_code, user_type="homeowner", sale_price=sale_price,product_id=product.id, user_id=i.user_id)
                        FranchisePinCodesPrice.objects.create(pin_code=i.pin_code, user_type="propertymanager", sale_price=sale_price, product_id=product.id, user_id=i.user_id)
                FranchisePrice.objects.filter(product_id=product.id,user_type="vacationer").update(sale_price=sale_price)
                FranchisePrice.objects.filter(user_type="homeowner",product_id=product.id).update(sale_price=sale_price)
                FranchisePrice.objects.filter(user_type="propertymanager",product_id=product.id).update(sale_price=sale_price)
                FranchisePrice.objects.filter(product_id=product.id).update(zero_seven_days="", greaterthan_seven="", zero_seven_days_wholesale="", greaterthan_seven_wholesale="")
                # return redirect('edit_product', slug)
            if product_quantity:
                cat_id = ProductCategory.objects.get(id=category)
                SKU_CODE = cat_id.name.upper()[0:2] + name.upper()[0:3] + "00"
                digits = 1
                sku_code = SKU_CODE
                all_product = ProductSkuCodes.objects.all()
                skuList = []
                for i in all_product:
                    spilts = i.sku_code
                    Str = spilts[:-1]
                    if sku_code == Str:
                        skuList.append(Str)
                count = len(skuList)
                for j in range(0, int(product_quantity)):
                    if ProductSkuCodes.objects.filter(sku_code=sku_code + str(digits)):
                        ProductSkuCodes.objects.create(
                            product_id=product.id, sku_code=sku_code + str(int(count + 1))
                        )
                        count += 1
                    else:
                        ProductSkuCodes.objects.create(
                            product_id=product.id, sku_code=sku_code + str(digits)
                        )
                        digits += 1
            messages.success(request, "Product update successfully !!!!")
            return redirect("/admin/product/")
        # category = ProductCategory.objects.all()
        subcategory = ProductSubCategory.objects.filter(category_id=product.category_id)
        categorys=ProductCategory.objects.all()
        user = User.objects.filter(roll="franchise")
        propertymanager = User.objects.filter(propertymanager_negotiable="1")
        return render(
            request,
            template_name,
            {
                "franchise_price":franchise_price,
                "franchise":franchise,
                "product":product,
                "subcategory": subcategory,"categorys":categorys,
                "franchise_user": user,"franchiseuser":franchiseuser,
                "propertymanager": propertymanager,
            },
        )
    except:
        return redirect("/admin/edit-product/" + str(slug))

def pin_code_ajax(request):
    if request.method == "POST":
        pincode=request.POST.getlist('pincode[]')
        product=request.POST.get('product') 
        data=FranchisePinCodesPrice.objects.filter(pin_code__in=pincode,product_id=product)
                  
        return render(request, 'admin/ProductManagement/edit_pincode_price.html', {"product_price": data})
     


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def EditProductPrice(request, slug):
    template_name = "admin/ProductManagement/edit_product_price.html"
    product=Product.objects.get(slug=slug)
    try:
        
        product_price=FranchisePinCodesPrice.objects.filter(product_id=product.id)   
        if request.method == 'POST':
            data=request.POST
            count=data.get('count')
            data_list = []
            selected_pin_code = []
            if count:
                is_valid = True
                bulk_update_data = []
                for i in range(int(count)):
                    pin_code = data.get(f'pin_code{i}', None)
                    user_type = data.get(f'user_type{i}', None)
                    user_id = data.get(f'user_id{i}', None)
                    
                    day_price = data.get(f'day_price{i}', None) 
                    days_price = data.get(f'days_price{i}', None)
                    wholesale = data.get(f'wholesale{i}', None)

                    wholesale_greaterthan = data.get(f'wholesale_greaterthan{i}', None)
                    sale_price = data.get(f'sale_price{i}', None) 
                    
                                    
                    selected_pin_code.append(data.get(f'pin_code{i}'))
                    if product.is_return == 1 :
                       
                        data_list.append({
                            'pin_code': data.get(f'pin_code{i}', None),
                            'user_type': data.get(f'user_type{i}', None),
                            'user_id':data.get(f'user_id{i}',None),
                            'zero_seven_days': data.get(f'day_price{i}', None),
                            'greaterthan_seven': data.get(f'days_price{i}', None),
                            'zero_seven_days_wholesale': data.get(f'wholesale{i}', None),
                            'greaterthan_seven_wholesale': data.get(f'wholesale_greaterthan{i}', None),
                        })

        
                    
                        pincode_price = FranchisePinCodesPrice.objects.filter(product_id=product.id, pin_code = pin_code, user_type = user_type)
                        pincode_price.update(zero_seven_days = day_price,greaterthan_seven = days_price,zero_seven_days_wholesale=wholesale,
                        greaterthan_seven_wholesale = wholesale_greaterthan)
                    else:
                        data_list.append({
                            'pin_code': data.get(f'pin_code{i}', None),
                            'user_type': data.get(f'user_type{i}', None),
                            'user_id':data.get(f'user_id{i}',None),
                            'sale_price': data.get(f'sale_price{i}', None),
                            
                        })
                        pincode_price = FranchisePinCodesPrice.objects.filter(product_id=product.id, pin_code = pin_code, user_type = user_type)
                        pincode_price.update(sale_price=sale_price)

                messages.success(request,'Successfully updated.')
                return render(request, template_name, {'is_edit': True, 'pincode_price': data_list, "product_price":product_price, 'product':product, 'selected_pin_code': selected_pin_code})                   
        return render(request, template_name, {"product_price":product_price,'product':product})
    except:
        messages.error(request,'Something Went Wrong!!')
        return redirect('/admin/edit-product-price/' + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_product_ajax(request):
    product = Product.objects.all()
    if request.method == "POST":
        user_ids = request.POST.getlist("info_user[]")
        input_count = int(request.POST.get("input_count"))
        user_type = request.POST.get("user_type")
        product_id = request.POST.get("product_id")
        get_pincode = FranchisePinCodes.objects.filter(user_id__in=user_ids)
        j = input_count
        for i in get_pincode:
            j = j + 1
            i.pincode_index = j
            i.user_type = user_type

        get_pincode_price = FranchisePinCodesPrice.objects.filter(
            user_id__in=user_ids, product_id=product_id, user_type=user_type
        )

        # j = input_count
        # for i in get_pincode:
        #     j = j + 1
        #     i.pincode_index = j
        #     i.user_type = user_type

        # fetch_franchise_price_data = FranchisePinCodesPrice.objects.filter(
        #     user_id__in=user_ids, product_id__in=product
        # )
        return render(
            request,
            "admin/ProductManagement/edit_vacationer_product_pincode.html",
            {
                "user": get_pincode,
                "get_pincode_price": get_pincode_price
                # "fetch_franchise_price_data": fetch_franchise_price_data,
            },
        )
    return JsonResponse({"status": "error"})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def negotiable_price_ajax(request):
    if request.method == "POST":

        user = request.POST.getlist("userIDS[]")
        get_pincode = FranchisePinCodes.objects.filter(user_id__in=user)

        return render(
            request,
            "admin/ProductManagement/product_detail.html",
            {"user": get_pincode},
        )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect("/admin/product/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_product(request, slug):
    category = ProductCategory.objects.all()
    subcategory = ProductSubCategory.objects.all()
    product = Product.objects.get(slug=slug)
    return render(
        request,
        "admin/ProductManagement/view_product.html",
        {"category": category, "product": product, "subcategory": subcategory},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def product_status_change_detail(request, slug):
    try:
        category = ProductCategory.objects.all()
        subcategory = ProductSubCategory.objects.all()
        product = Product.objects.get(slug=slug)
        if request.method == "POST":
            status = request.POST.get("status")
            if status == "True":
                product.is_active = False
            else:
                product.is_active = True
            product.save()
            messages.success(request, "Status Changed Successfully")
            return redirect("/admin/product_status_change_detail/" + str(slug))
        return render(
            request,
            "admin/ProductManagement/view_product.html",
            {"category": category, "product": product, "subcategory": subcategory},
        )
    except:
        messages.error(request, "Something Went Wrong")
        return redirect("/admin/product_status_change_detail/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def fetch_product_option(request):
    if request.method == "POST":
        try:
            option_id = request.POST.get("option_id")
            data = Options_value.objects.filter(option_id=option_id).values()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Details Submitted Successfully !!!!",
                    "data": list(data),
                },
                status=200,
            )
        except:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Something went wrong",
                },
                status=404,
            )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def fetch_product_option_value(request):
    if request.method == "POST":
        option_value = request.POST.get("option_value")
        data = Options_value.objects.filter(id=option_value).values()
    return JsonResponse(
        {
            "status": "success",
            "message": "Details Submitted Successfully !!!!",
            "data": list(data),
        },
        status=200,
    )


#  Superadmin and Subadmin forgot password:
@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            data = User.objects.get(email=email)
            if data is None:
                messages.error(request, "Invalid email !!!! ")
                return redirect("/admin/forgot-password/")
            elif data.is_superuser:
                otp = generateOTP()
                data.OTP = otp
                data.save()
                send_to = [email]
                subject = "Forgot Password"
                content = "This is your One Time Password " + otp
                sendMail(subject, content, send_to)
                messages.success(request, "OTP send Successfully !!!! ")
                return redirect("/admin/forgot-otp/" + str(data.slug))
            elif data.roll == "subadmin":
                otp = generateOTP()
                data.OTP = otp
                data.save()
                send_to = [email]
                subject = "Forgot Password"
                content = "This is your One Time Password " + otp
                sendMail(subject, content, send_to)
                messages.success(request, "OTP send Successfully !!!! ")
                return redirect("/admin/forgot-otp/" + str(data.slug))
            else:
                messages.error(request, "Invalid email !!!! ")
                return redirect("/admin/forgot-password/")
        except:
            messages.error(request, "Invalid email !!!! ")
            return redirect("/admin/forgot-password/")
    return render(request, "admin/auth/forget_password.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def forgot_otp(request, slug):
    if request.method == "POST":
        otp = request.POST.get("otp")
        try:
            data = User.objects.get(slug=slug)
            if data is None:
                messages.error(request, "OTP Not Matched !!!! ")
                return redirect("/admin/forgot-otp/" + str(data.slug))
            elif data.OTP == otp:
                messages.success(request, "OTP matched Successfully !!!! ")
                return redirect("/admin/forgot-password-form/" + str(data.slug))
            else:
                messages.error(request, "OTP Not Matched !!!! ")
                return redirect("/admin/forgot-otp/" + str(data.slug))
        except:
            messages.error(request, "Something went wrong !!!! ")
            return redirect("/admin/forgot-otp/" + str(data.slug))

    return render(request, "admin/auth/forgot-otp.html", {"slug": slug})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
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


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def forgot_password_form(request, slug):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        try:
            if new_password == confirm_password:
                pssword = User.objects.get(slug=slug)
                pssword.password = make_password(new_password)
                pssword.OTP = ""
                pssword.save()

                messages.success(request, "Password Change successfully !!!! ")
                return redirect("/admin/")
            else:
                messages.error(request, "Password Does not match !!!! ")
                return redirect("/admin/forgot-password-form/" + str(slug))
        except:
            messages.error(request, "Something went wrong !!!! ")
            return redirect("/admin/forgot-password-form/" + str(slug))

    return render(request, "admin/auth/forgot-password-form.html")


# Offer Management CURD:
@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def offer(request):
    offer_data = OfferManagement.objects.all().order_by("-id")
    return render(
        request, "admin/offermanagement/offer.html", {"offer_data": offer_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def offer_add(request):
    try:
        category = ProductCategory.objects.all()
        if request.method == "POST":
            category = request.POST.get("category")

            name = request.POST.get("name")
            image = request.FILES.get("image")
            discount = request.POST.get("discount")
            term = request.POST.get("terms")
            validity = request.POST.get("validity")

            status = request.POST.get("status")

            category_name=ProductCategory.objects.get(id=category)
            code_name=name.upper()[0:3]+category_name.name.upper()[0:2]+discount
            
            if OfferManagement.objects.filter(code=code_name).exists():
                messages.error(request, "This Code already exist please change discount or category name !!!")
                return redirect("offer_add")

            offer = OfferManagement.objects.create(
                category_id=category,
                offer_name=name,
                offer_image=image,
                offer_discount=discount,
                offer_terms_condition=term,
                offer_validity=validity,
                is_active=status,code=code_name
            )

            offer.save()
            messages.success(request, "Offer Successfully Add!!!")
            return redirect("offer")
        return render(
            request, "admin/offermanagement/offer_add.html", {"category": category}
        )
    except:
        messages.error(request, "Something Went Wrong!!!")
        return redirect("offer_add")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def offer_edit(request, slug):
    try:
        category = ProductCategory.objects.all()
        edit_offer = OfferManagement.objects.get(slug=slug)
    
        if request.method == "POST":
            category = request.POST.get("category")

            name = request.POST.get("name")
            image = request.FILES.get("image")
            discount = request.POST.get("discount")

            term = request.POST.get("terms")

            validity = request.POST.get("validity")
            status = request.POST.get("status")

            category_name=ProductCategory.objects.get(id=category)
            code_name=name.upper()[0:3]+category_name.name.upper()[0:2]+discount
            # if OfferManagement.objects.filter(code=code_name).exists():
            #     messages.error(request, "This code already exist on this category !!!")
            #     return redirect("/admin/offer-edit/" + str(slug))

            edit_offer.category_id = category
            edit_offer.offer_name = name
            if image:
                edit_offer.offer_image = image
            edit_offer.offer_discount = discount

            edit_offer.offer_terms_condition = term
            edit_offer.offer_validity = validity
            edit_offer.is_active = status
            edit_offer.code = code_name

            edit_offer.save()
            messages.success(request, "Update Successfuly Done!!!")
            return redirect("offer")
        return render(
        request,
        "admin/offermanagement/offer_edit.html",
        {"category": category, "edit_offer": edit_offer},
    )
    except:
        messages.error(request, "This Code already exist please change discount or category name!!!")
        return redirect("/admin/offer-edit/" + str(slug))

    


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_offer(request, slug):
    category = ProductCategory.objects.all()
    offer = OfferManagement.objects.get(slug=slug)
    return render(
        request,
        "admin/offermanagement/offer_view_detail.html",
        {"category": category, "offer": offer},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def offer_delete(request, id):
    offer = OfferManagement.objects.get(id=id)
    offer.delete()
    messages.error(request, "Delete Successfully!!!")
    return redirect("offer")


# Option Management CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def option(request):
    option = Options.objects.all()
    return render(request, "admin/option management/option.html", {"option": option})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_option(request):
    if request.method == "POST":
        name = request.POST.get("name")
        is_active = request.POST.get("status")
        data = Options.objects.create(name=name, is_active=is_active)
        messages.success(request, "Option create Successfully!!!")
        return redirect("/admin/option/")
    return render(request, "admin/option management/add_option.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_option(request, slug):
    if request.method == "POST":
        name = request.POST.get("name")
        is_active = request.POST.get("status")
        data = Options.objects.get(slug=slug)
        data.name = name
        data.is_active = is_active
        data.save()
        messages.success(request, "Option Update Successfully!!!")
        return redirect("/admin/option/")
    option = Options.objects.get(slug=slug)
    return render(
        request, "admin/option management/edit_option.html", {"option": option}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def option_delete(request, id):
    option = Options.objects.get(id=id)
    option.delete()
    messages.error(request, "Delete Successfully!!!")
    return redirect("/admin/option/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def option_value(request):
    option_query = f"""
        select * from superadmin_options_value INNER JOIN superadmin_options on superadmin_options_value.option_id = superadmin_options.id GROUP BY option_id
    """
    option = Options_value.objects.raw(option_query)
    return render(
        request, "admin/option management/option_value.html", {"option": option}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_option_value(request):
    if request.method == "POST":
        count = request.POST.get("count")
        name = request.POST.get("name")
        option_key = request.POST.get(f"option[0]key")
        option_value = request.POST.get(f"option[0]value")
        if count:
            for i in range(int(count)):
                option_keys = request.POST.get(f"option[{i}]key")
                option_values = request.POST.get(f"option[{i}]value")
                data = Options_value.objects.create(
                    option_id=name,
                    option_name=option_keys,
                    option_value=option_values,
                    option_slug=option_key,
                )
            messages.success(request, "Option create Successfully!!!")
            return redirect("/admin/option_value/")
        else:
            data = Options_value.objects.create(
                option_id=name,
                option_name=option_key,
                option_value=option_value,
                option_slug=option_key,
            )
            messages.success(request, "Option create Successfully!!!")
            return redirect("/admin/option_value/")
    option = Options.objects.all()
    return render(
        request, "admin/option management/add_option_value.html", {"option": option}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_option_value(request, id):
    if request.method == "POST":
        count = request.POST.get("count")
        name = request.POST.get("name")

        data = Options_value.objects.filter(option_id=id).delete()
        if count:
            for i in range(int(count)):
                option_keys = request.POST.get(f"option[{i}]key")
                option_values = request.POST.get(f"option[{i}]value")
                if option_keys == None or option_values == None:
                    pass
                else:
                    data = Options_value.objects.create(
                        option_id=id,
                        option_name=option_keys,
                        option_value=option_values,
                    )
            messages.success(request, "Option create Successfully!!!")
            return redirect("/admin/option_value/")
    option = Options_value.objects.filter(option_id=id)
    options_count = Options_value.objects.filter(option_id=id).count()
    return render(
        request,
        "admin/option management/edit_option_value.html",
        {"option": option, "options_count": options_count},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_option_value(request, id):
    options = Options_value.objects.filter(option_id=id)
    options.delete()
    messages.error(request, "Delete Successfully!!!")
    return redirect("/admin/option_value/")


# FAQ CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def Faq(request):
    data = FAQ.objects.all()
    return render(request, "admin/FAQ/faq.html", {"data": data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_faq(request):
    try:
        if request.method == "POST":
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            if not (
                question and not question.isspace() and answer and not answer.isspace()
            ):
                messages.error(request, "All Fields Are Required")
                return redirect("add_faq")

            add_data = FAQ.objects.create(question=question, answer=answer)
            add_data.save()
            messages.success(request, "Successfully Add!!")
            return redirect("Faq")
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("add_faq")

    return render(request, "admin/FAQ/add_faq.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_faq(request, slug):
    try:
        edit_data = FAQ.objects.get(slug=slug)
        if request.method == "POST":
            question = request.POST.get("question")
            answer = request.POST.get("answer")

            if not (
                question and not question.isspace() and answer and not answer.isspace()
            ):
                messages.error(request, "All Fields Are Required")
                return redirect("/admin/edit-faq/" + str(slug))

            edit_data.question = question
            edit_data.answer = answer
            edit_data.save()
            messages.success(request, "Update Successfully Done !!")
            return redirect("Faq")
    except:
        messages.error(request, "Something Went Wrong !!")
        return redirect("/admin/edit-faq/" + str(slug))

    return render(request, "admin/FAQ/edit_faq.html", {"edit_data": edit_data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_faq(request, slug):
    view_data = FAQ.objects.get(slug=slug)
    return render(request, "admin/FAQ/view_faq.html", {"view_data": view_data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_faq(request, id):
    data = FAQ.objects.get(id=id)
    data.delete()
    messages.error(request, "Delete Successfully Done!!")
    return redirect("Faq")


# Blog Management CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def blog(request):
    blog = Blog.objects.all()
    return render(request, "admin/Blog Management/blog.html", {"blog": blog})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_blog(request):
    try:
        if request.method == "POST":
            blog_title = request.POST.get("blog_title")
            blog_image = request.FILES.get("blog_image")
            blog_video = request.FILES.get("blog_video")
            blog_content = request.POST.get("blog_content")
            meta_keyword = request.POST.get("meta_keyword")
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            if not (
                blog_title
                and not blog_title.isspace()
                and blog_image
                # and blog_content
                # and not blog_content.isspace()
                and meta_keyword
                and not meta_keyword.isspace()
                and meta_title
                and not meta_title.isspace()
                and meta_description
                and not meta_description.isspace()
            ):
                messages.error(request, "All Felids are Required")
                return redirect("add_blog")

            data = Blog.objects.create(
                blog_title=blog_title,
                blog_image=blog_image,
                blog_video=blog_video,
                blog_description=blog_content,
                meta_keyword=meta_keyword,
                meta_title=meta_title,
                meta_description=meta_description,
            )

            data.save()
            messages.success(request, "Blod Add Successfully Done!!")
            return redirect("blog")
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("add_blog")

    return render(request, "admin/Blog Management/add_blog.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_blog(request, slug):
    try:
        edit_data = Blog.objects.get(slug=slug)
        if request.method == "POST":
            blog_title = request.POST.get("blog_title")
            blog_image = request.FILES.get("blog_image")
            blog_content = request.POST.get("blog_content")
            meta_keyword = request.POST.get("meta_keyword")
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")
            blog_video = request.FILES.get("blog_video")

            # if not(blog_title and not blog_title.isspace() and blog_image and blog_content and not blog_content.isspace()
            # and meta_keyword and not meta_keyword.isspace() and meta_title and not meta_title.isspace() and meta_description
            # and not meta_description.isspace()):
            #     messages.error(request,"All Felids are Required")
            #     return redirect("/admin/edit-blog/" + str(slug))

            edit_data.blog_title = blog_title
            if blog_image:
                edit_data.blog_image = blog_image
            edit_data.blog_content = blog_content
            edit_data.meta_keyword = meta_keyword
            edit_data.meta_title = meta_title
            edit_data.meta_description = meta_description
            edit_data.blog_video= blog_video
            edit_data.save()

            messages.success(request, "Update Successfully Done!!")
            return redirect("blog")
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/edit-blog/" + str(slug))

    return render(
        request, "admin/Blog Management/edit_blog.html", {"edit_data": edit_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_blog(request, slug):
    view_data = Blog.objects.get(slug=slug)
    return render(
        request, "admin/Blog Management/view_blog.html", {"view_data": view_data}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_blog(request, id):
    data = Blog.objects.get(id=id)
    data.delete()
    messages.error(request, "Delete Successfully Done!!")
    return redirect("blog")


# Sub Category CURD:


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def subcategory(request):
    subcategory = ProductSubCategory.objects.all()
    return render(
        request,
        "admin/ProductManagement/subcategory.html",
        {"subcategory": subcategory},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_subcategory(request):
    try:
        if request.method == "POST":
            category = request.POST.get("category")
            name = request.POST.get("name")
            image = request.FILES.get("image")
            is_active = request.POST.get("status")

            subcategory_data = ProductSubCategory.objects.create(
                category_id=category,
                name=name,
                subcategory_image=image,
                is_active=is_active,
            )
            subcategory_data.save()
            messages.success(request, "Sub Category Add Successfully Done!!")
            return redirect("subcategory")

    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("add_subcategory")

    category = ProductCategory.objects.all()
    return render(
        request, "admin/ProductManagement/add_subcategory.html", {"category": category}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_subcategory(request, slug):
    try:
        category = ProductCategory.objects.all()
        data = ProductSubCategory.objects.get(slug=slug)
        if request.method == "POST":
            category = request.POST.get("category")
            name = request.POST.get("name")
            image = request.FILES.get("image")
            is_active = request.POST.get("status")

            data.category_id = category
            data.name = name
            if image:
                data.subcategory_image = image
            data.is_active = is_active

            data.save()
            messages.success(request, "Update Succesfully Done !!")
            return redirect("/admin/edit-subcategory/" + str(slug))

    except:
        messages.error(request, "Something Went Wrong !!")
        return redirect("/admin/edit-subcategory/" + str(slug))

    return render(
        request,
        "admin/ProductManagement/edit_subcategory.html",
        {"category": category, "data": data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def view_subcategory(request, slug):
    category = ProductCategory.objects.all()
    view_data = ProductSubCategory.objects.get(slug=slug)
    return render(
        request,
        "admin/ProductManagement/view_subcategory.html",
        {"category": category, "view_data": view_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_subcategory(request, id):
    data = ProductSubCategory.objects.get(id=id)
    data.delete()
    messages.error(request, "Delete Successfully Done!!")
    return redirect("subcategory")


from django.db.models import Q


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
# Report Management:
def report(request):
    user_id = request.GET.get("user_id")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    if user_id or start_date or end_date:
        if user_id == "all":
            data = User.objects.filter().exclude(roll="superadmin")
            return render(
                request, "admin/Report Management/user_report.html", {"data": data}
            )
        if user_id and start_date and end_date:
            data = User.objects.filter(
                Q(created_at=start_date) | Q(created_at=end_date), roll=user_id
            )
            return render(
                request, "admin/Report Management/user_report.html", {"data": data}
            )
        else:
            data = User.objects.filter(roll=user_id)
            return render(
                request, "admin/Report Management/user_report.html", {"data": data}
            )

    data = User.objects.filter().exclude(roll="superadmin")
    return render(request, "admin/Report Management/user_report.html", {"data": data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def generate_pdf(request, id):
    view_detail_data = User.objects.get(slug=id)
    return render(
        request,
        "admin/Report Management/generate_pdf.html",
        {"view_detail_data": view_detail_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def user_data_pdf(request, slug):
    value = User.objects.get(slug=slug)
    # getting the template
    pdf = html_to_pdf("admin/Report Management/download.html", {"value": value})
    # rendering the template
    return HttpResponse(pdf, content_type="application/pdf")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def notification(request):

    notification = request.GET.get("notification_id")

    if notification:
        data = User.objects.filter(roll=notification)
        data1 = serializers.serialize(
            "json",
            data,
            fields=(
                "id",
                "first_name",
                "last_name",
                "email",
                "roll",
                "mobile_number",
                "slug",
            ),
        )
        return JsonResponse(
            {
                "status": "success",
                "message": "Details Submitted Successfully !!!!",
                "data": data1,
            },
        )

    else:

        not_data = User.objects.filter().exclude(roll="superadmin")
        return render(
            request,
            "admin/Notification Management/notifications.html",
            {"not_data": not_data},
        )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def delete_notification(request, slug):
    data = Notification.objects.get(slug=slug)

    data.delete()

    messages.error(request, "Delete Successfully Done !!")
    return redirect("notification")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def email_notification(request):
    if request.method == "POST":
        emails = request.POST.getlist("emails[]")
        messages = request.POST.get("messagess")
        content = strip_tags(messages)
        subject = "Email  NOtification"
        recipient_list = emails
        EmailThread(subject, content, recipient_list).start()
        return JsonResponse(
            {"success": "True", "message": "Email Notification Sent Successfully !!!!"}
        )
    else:
        return JsonResponse({"success": "False", "message": "Email is not working"})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def request_products_list(request):
    product = RequestProduct.objects.all()

    return render(
        request,
        "admin/RequestManagement/request_product_list.html",
        {
            "product": product,
        },
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_pages(request, slug):
    try:
        if request.method == "POST":
            title = request.POST.get("title")
            content = request.POST.get("content")
            image = request.FILES.get("image")
            text1 = request.POST.get("text1")
            text2 = request.POST.get("text2")
            text3 = request.POST.get("text3")
            if (
                image is None
                and title is None
                and text1 is None
                and text2 is None
                and text3 is None
            ):
                data = pages.objects.filter(slug=slug).update(
                    image=image,
                )

                messages.success(request, "Pages is updated ")
                return redirect("/admin/pages")
            elif image is None and title:
                if content and text1 and text2 and text3:
                    data = pages.objects.get(slug=slug)
                    data.title = title
                    data.content = content
                    data.text1 = text1
                    data.text2 = text2
                    data.text3 = text3
                    data.save()
                    messages.success(request, "Pages is updated ")
                    return redirect("/admin/pages")
                if text1 and text2 and text3:
                    data = pages.objects.get(slug=slug)
                    data.title = title
                    data.text1 = text1
                    data.text2 = text2
                    data.text3 = text3
                    data.save()
                    messages.success(request, "Pages is updated ")
                    return redirect("/admin/pages")
                data = pages.objects.get(slug=slug)
                data.title = title
                data.save()
                messages.success(request, "Pages is updated ")
                return redirect("/admin/pages")
            elif image and title:
                data = pages.objects.get(slug=slug)
                data.title = title
                data.image = image
                data.save()
                messages.success(request, "Pages is updated ")
                return redirect("/admin/pages")
            else:
                data = pages.objects.get(slug=slug)
                data.image = image
                data.save()
                messages.success(request, "Pages is updated ")
                return redirect("/admin/pages")
        data = pages.objects.get(slug=slug)
        return render(request, "admin/cms-pages/add_page.html", {"data": data})
    except:
        messages.error(request, "Something went wrong ")
        return redirect("/admin/add_pages/" + slug)


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def cms_page(request):
    data = pages.objects.all()
    return render(request, "admin/cms-pages/pages.html", {"data": data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_coupon(request):
    return render(request, "admin/coupon/add-coupon.html")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def appbanner(request):
    data = AppBanner.objects.all()
    return render(request, "admin/app-banner/app_banner.html", {"data": data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def edit_appbanner(request, slug):
    # try:
    appbanner = AppBanner.objects.get(slug=slug)
    if request.method == "POST":
        title = request.POST.get("title")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        content = request.POST.get("content")
        a = get_size(video)
        if float(a) > float(20.0):
            messages.error(request, "Video size is less then 20 mb !!!")
            return redirect("/admin/edit-appbanner/" + slug)
        if image is None or video is None:
            if image:
                appbanner.title = title
                appbanner.content = content
                appbanner.image = image
                appbanner.save()
            elif video:

                appbanner.title = title
                appbanner.content = content
                appbanner.video = video
                appbanner.save()
            elif image is None:
                appbanner.title = title
                appbanner.content = content
                appbanner.save()

            elif video is None:
                appbanner.title = title
                appbanner.content = content
                appbanner.save()
        else:
            appbanner.title = title
            appbanner.content = content
            appbanner.image = image
            appbanner.video = video
            appbanner.save()
        messages.success(request, "updated successfully !!!")
        return redirect("/admin/appbanner")
    return render(
        request, "admin/app-banner/edit_app_banner.html", {"appbanner": appbanner}
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def aboutUs(request):
    try:
        data = AboutUs.objects.get(id=1)
        if request.method == "POST":
            heading = request.POST.get("heading")
            sub_heading = request.POST.get("subheading")
            description1 = request.POST.get("description1")
            description2 = request.POST.get("description2")
            description2_image = request.FILES.get("image")

            description3 = request.POST.get("description3")
            if description2_image == None:
                data.heading = heading
                data.sub_heading = sub_heading
                data.description1 = description1
                data.description2 = description2
                data.description3 = description3
                data.save()
            else:
                data.heading = heading
                data.sub_heading = sub_heading
                data.description1 = description1
                data.description2 = description2
                data.description3 = description3
                data.image = description2_image
                data.save()
            messages.success(request, "updated successfully !!!")
            return redirect("/admin/about-us/")
        return render(request, "admin/about/about.html", {"data": data})
    except:
        messages.error(request,'Something Went Wrong!!')
        return redirect("/admin/dashboard/")


# def Blog(request):

#     return render(request, "admin/distance/distance.html")

# except:
#     messages.success(request, "Something went wrong")
#     return redirect("/admin/edit-appbanner/" + str(slug))


# def Distance(request):
#     data = ProductDistance.objects.all()
#     return render(request, "admin/distance/distance.html", {"data": data})


# def EditDistance(request, slug):
#     if request.method == "POST":
#         distance = request.POST.get("distance")
#         distance_save = ProductDistance.objects.get(slug=slug)
#         distance_save.distance = distance
#         distance_save.save()
#         messages.success(request, "dDstance is updated successfully !!!")
#         return redirect("/admin/distance/")
#     data = ProductDistance.objects.get(slug=slug)
#     return render(request, "admin/distance/edit-distance.html", {"data": data})


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def add_company(request):
    try:
        data = request.POST
        if request.method == "POST":

            companyname = request.POST.get("companyname")

            companyemail = request.POST.get("companyemail")
            companycontact = request.POST.get("company_contact")

            companyaddress = request.POST.get("companyaddress")

            company_zip = request.POST.get("company_zip")
            if PropertyManagerMember.objects.filter(companyzip_code=company_zip).exists():
                messages.error(request, "Zip Code already Exist")
                return render(
                    request, "admin/UserManagement/company_add.html", {"data": data}
                )

            data = PropertyManagerMember.objects.create(
                companyname=companyname,
                companyemail=companyemail,
                companyaddress=companyaddress,
                companyzip_code=company_zip,
                companycontact=companycontact,
                is_verified=True,
            )
            messages.success(request, "Company Register Successfully!!")
            return redirect("/admin/company_listing/")
 

        return render(request, "admin/UserManagement/company_add.html", {"data": data})
    except:
        messages.error(request,'Something Went wrong!!')
        return redirect("/admin/add/company/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def company_listing(request):
    company_data = PropertyManagerMember.objects.all()
    return render(
        request,
        "admin/UserManagement/company_listing.html",
        {"company_data": company_data},
    )


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def company_edit(request, slug):
    try:
        company_data = PropertyManagerMember.objects.get(slug=slug)
        if request.method == "POST":

            companyname = request.POST.get("companyname")

            companyemail = request.POST.get("companyemail")
            companycontact = request.POST.get("company_contact")

            companyaddress = request.POST.get("companyaddress")

            company_zip = request.POST.get("company_zip")

            company_data.companyname = companyname
            company_data.companyemail = companyemail
            company_data.companycontact = companycontact
            company_data.companyaddress = companyaddress
            company_data.is_verified = True

            company_data.companyzip_code = company_zip

            company_data.save()

            messages.success(request, "Company Update Successfully!!")
            return redirect("/admin/company_listing/")

        return render(
            request,
            "admin/UserManagement/company_edit.html",
            {"company_data": company_data},
        )
    except:
        messages.error(request, "zip code allready exits!!")
        return redirect("/admin/company/edit/" + str(slug))


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def company_delete(request, id):
    try:
        company_data = PropertyManagerMember.objects.get(id=id)
        company_data.delete()
        messages.error(request, "Company Delete successfully!!")
        return redirect("/admin/company_listing/")
    except:
        messages.error(request, "Something Went Wrong!!")
        return redirect("/admin/company_listing/")


@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def company_view(request, slug):
    company_data = PropertyManagerMember.objects.get(slug=slug)
    return render(
        request,
        "admin/UserManagement/company_view.html",
        {"company_data": company_data},
    )



@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def excel_skucode(request):
    if request.method=="POST":
        product_id=request.POST.getlist('products[]')
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="SkuCode.xlsx"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sku_Code')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Category', 'Subcategory', 'Product Name','SKU CODE','Product-ID']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rows = ProductSkuCodes.objects.filter(product_id__in=product_id).values_list('product__category__name', 'product__subcategory__name','product__name','sku_code','product_id')
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response

@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def import_excel(request):
    if request.method == "POST":
        excel_file = request.FILES.get("excelfile")
        u=pd.read_excel(excel_file) #, engine='openpyxl'
        data_frame = pd.DataFrame(u, columns=['ID', 'Product-ID', 'SKU CODE'])
        data_frame_dict = data_frame.to_dict(orient='records')
        product=u['Product-ID']
      
        sku_code=u['SKU CODE']
        products = np.array(product, dtype=np.int64)
       
        sku = np.array(sku_code)
        ProductSkuCodes.objects.filter(product_id__in=products).delete()
        sku_list = []

        for i in data_frame_dict:
            sku_list.append(ProductSkuCodes(product_id=i['Product-ID'], sku_code=i['SKU CODE']))
        
        ProductSkuCodes.objects.bulk_create(sku_list)

        messages.success(request,'Data import Successfully Done!')
        return redirect('/admin/product/')


       
   

@login_required(login_url="/admin/")
@user_passes_test(lambda user: user.is_superuser)
def orderlist(request):
    order_list=OrderManagement.objects.all().order_by('-id')
    return render(request, "admin/Order_Management/order.html",{"order_data":order_list})

def AddOrder(request):
    # try:
        products=Product.objects.filter(is_active=True)
        company=PropertyManagerMember.objects.filter(is_verified="1")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        seven_days = datetime.date.today() + datetime.timedelta(days=7)
        zip_code=FranchisePinCodes.objects.all()
        if request.method == "POST":
            user_type=request.POST.get('user-type')
            pin_code=request.POST.get('zip-code')
            user_id=request.POST.get('user')
            product_id=request.POST.getlist('products[]')
            offer_id=request.POST.get('offer')
            delivery_date=request.POST.get('delivery-date')
            return_date=request.POST.get('return-date')
            actual=request.POST.get('actual')
            effective=request.POST.get('effective')
            address=request.POST.get('address')
            gate=request.POST.get('gate')
            door_code=request.POST.get('door_code')
            company_id=request.POST.get('user-company')
           
            reservation_number=request.POST.get('reservation_number')
            subdivision=request.POST.get('subdivision')
            notes=request.POST.get('notes')
            product_quantity_data = json.loads(request.POST.get('product_quantity_data'))
            check_product_quantity=list(product_quantity_data.values())
            order_id=createorderid()
            product_price=ProductPrice(user_type,pin_code,product_id,delivery_date,return_date)
            product_data=Product.objects.filter(id__in=product_id)
            product_category=Product.objects.filter(id__in=product_id).values_list('category_id')
            if return_date < delivery_date:
                messages.error(request,'Return date should be greater than to delivery date')
                return redirect("orderlist")

            for qty in check_product_quantity:
                if Product.objects.filter(id__in=product_id,quantity__lte=qty):
                    messages.error(request,'Quantity Not Available please add minimum quantity')
                    return redirect("orderlist")
            if offer_id:
                offer_discount=OfferManagement.objects.get(code=offer_id)
            product_detail = []
            data = []
            for j,i in enumerate(product_data):
                if product_price[j].get('zero_seven_days'):
                    price = product_price[j].get('zero_seven_days') 
                    
                elif product_price[j].get('sale_price'):
                    price = product_price[j].get('sale_price')
                
                elif product_price[j].get('zero_seven_days_wholesale'):
                    price = product_price[j].get('zero_seven_days_wholesale')

                data.append({
                    "product_id": i.id,
                    "product_name":i.name,
                    "product_category":i.category.name,
                    "price": price,
                    "product_return":i.is_return,
                    "product_quantity": product_quantity_data.get(str(i.id))
                })
            if offer_id:
                offer_discount=OfferManagement.objects.get(code=offer_id)
            
                order=OrderManagement.objects.create(user_id=user_id,order_id=order_id,
                product_details=data, order_return=return_date,pin_code=pin_code, delivery=delivery_date, user_type=user_type,company_id=company_id,
                actual_price=actual, discount_price=effective, order_created_by="admin", order_status="pending", payment_status="0", offer_id=offer_discount.id,Address=address, gate=gate, subdivision=subdivision, reservationnumber=reservation_number,doorcode=door_code, notes=notes)
            else:
                order=OrderManagement.objects.create(user_id=user_id,order_id=order_id,product_details=data, user_type=user_type,company_id=company_id,
                order_return=return_date, delivery=delivery_date,pin_code=pin_code, actual_price=actual, 
                order_created_by="admin", order_status="pending", discount_price=actual,payment_status="0",Address=address, gate=gate, subdivision=subdivision, reservationnumber=reservation_number,doorcode=door_code, notes=notes)
            user=User.objects.get(id=user_id)
        
            subject = " Welcome to   Honest Sherpa world"
            message = f"Hi {user.first_name} {user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_id} and Your paymemt status is Pending "
            recipient_list = [user.email]
            sendMail(subject, message,recipient_list)
            messages.success(request,'Order Create Succesfully')
            return redirect('/admin/order-list/')
        context={
            "products":products,"tomorrow":tomorrow,"seven_days":seven_days,"zip_code":zip_code,"company":company
        }
        return render(request, "admin/Order_Management/order_add.html",context)
    # except:
    #     messages.error(request,'Something Went Wrong!!')
    #     return redirect('/admin/order-list/')

   
def select_User(request):
    try:
        if request.method == "POST":
            user_type=request.POST.get('user_type')
        
            user_list=User.objects.filter(roll=user_type).values()
            return JsonResponse(
                    {
                        "status": "success",
                        "message": "Details Submitted Successfully !!!!",
                        "data": list(user_list),
                    },
                    status=200,
                )
    except:
        return JsonResponse(
                    {
                        "status": "error",
                        "message": "something Went Wrong !!!!",
                    },
                    status=400,
                )



def select_product(request):
    try:
        if request.method == "POST":
            product_id=request.POST.getlist('product_id[]')
            user_type=request.POST.get('user_type')
            zip_code=request.POST.get('zip_code')
            product_data=eval(request.POST.get("product_data"))
            product_list=Product.objects.filter(id__in=product_id).values("category_id")
            product_category_list=[]

            for i in range(len(product_list)):
                for key in product_list[i]:
                    product_category_list.append(product_list[i][key])
            code_list=OfferManagement.objects.filter(category_id__in=product_category_list,offer_validity__gte=datetime.date.today()).values()
            result_data = calculate_order_price(zip_code,product_id,user_type,product_data=product_data)
            return JsonResponse(
                    {
                        "status": "success",
                        "message": "Details Submitted Successfully !!!!",
                        "data":list(code_list),
                        'response':result_data,
                    },
                    status=200,
                )
        return JsonResponse(
                    {
                        "status": "error",
                        "message": "something Went Wrong !!!!",
                    },
                    status=400,
                )
    except:
        return JsonResponse(
                    {
                        "status": "error",
                        "message": "something Went Wrong !!!!",
                    },
                    status=400,
                )


def select_pincode(request):
    # try:
        if request.method == "POST":
            user_type=request.POST.get('user_type')
            zip_code=request.POST.get('zip_code')
            products=FranchisePinCodesPrice.objects.filter(user_type=user_type,pin_code=zip_code).values_list('product_id', flat=True)
            product=Product.objects.filter(id__in=products).values()     
            return JsonResponse(
                    {
                        "status": "success",
                        "message": "Details Submitted Successfully !!!!",
                        # "data":actual_price,
                        "data":list(product),
                    },
                    status=200,
            )
    # except:
    #     return JsonResponse(
    #                 {
    #                     "status": "error",
    #                     "message": "something Went Wrong !!!!",
    #                 },
    #                 status=400,
    #             )

def change_date(request):
    # try:
        if request.method == "POST":
            user_type=request.POST.get('user_type')
            zip_code=request.POST.get('zip_code')
            product_id=request.POST.getlist('product_id[]')
            delivery_date=request.POST.get('delivery_date')
          
            return_date=request.POST.get('return_date')
           
            product_data=eval(request.POST.get("product_data"))
            default_date_dffrence=7
            delivery_convert_date = datetime.datetime.strptime(delivery_date, '%Y-%m-%d').date()
            if return_date:
                return_convert_date = datetime.datetime.strptime(return_date, '%Y-%m-%d').date()
                days_diffrence=return_convert_date-delivery_convert_date
                days_diffrence_count=int('{}'.format(days_diffrence.days))
            result_data=calculate_order_price(zip_code,product_id,user_type,days_diffrence=days_diffrence_count, product_data=product_data)  
            return JsonResponse(
                    {
                        "status": "success",
                        "message": "Details Submitted Successfully !!!!",
                        "data":result_data,
                    },
                    status=200,
            )
    # except:
    #     return JsonResponse(
    #                 {
    #                     "status": "error",
    #                     "message": "something Went Wrong !!!!",
    #                 },
    #                 status=400,
    #             )

def select_offer(request):
    # try:
        if request.method == "POST":
            user_type=request.POST.get('user_type')
            zip_code=request.POST.get('zip_code')
            product_id=request.POST.getlist('product_id[]')
            actual_price=request.POST.get('actual_price')
            offer=request.POST.get('offer')
            delivery_date=request.POST.get('delivery_date')
            return_date=request.POST.get('return_date')
            product_data=eval(request.POST.get("product_data"))
            default_date_dffrence=7
            delivery_convert_date = datetime.datetime.strptime(delivery_date, '%Y-%m-%d').date()
            if return_date:
                return_convert_date = datetime.datetime.strptime(return_date, '%Y-%m-%d').date()
                days_diffrence=return_convert_date-delivery_convert_date
                days_diffrence_count=int('{}'.format(days_diffrence.days))
            result_data=calculate_order_price(zip_code,product_id,user_type,offer=offer,days_diffrence=days_diffrence_count,product_data=product_data)
            result=round(float(actual_price)-float(result_data),2)

        return JsonResponse(
                {
                    "status": "success",
                    "message": "Details Submitted Successfully !!!!",
                    "data":result,           
                },
                status=200,
        )
    # except:
    #     return JsonResponse(
    #                 {
    #                     "status": "error",
    #                     "message": "something Went Wrong !!!!",
    #                 },
    #                 status=400,
    #             )


def orderView(request,slug):
    template_name = "admin/Order_Management/order_view_details.html"
    order_details=OrderManagement.objects.get(slug=slug)
    product_count=len(order_details.product_details)
    product_id_list=[]
    for i in order_details.product_details:
        product_id_list.append(i.get("product_id"))
    product_detail=Product.objects.filter(id__in=product_id_list)
   
    
    return render(request, template_name, {'order_details':order_details, 'product_count':product_count, 'product_detail':product_detail})


def changeActualPrice(request):
    if request.method == "POST":
        user_type=request.POST.get("user_type")
        zip_code=request.POST.get("zip_code")
        product_data=eval(request.POST.get("product_data"))
        product_ids = product_data.keys()
        result_data = calculate_order_price(zip_code,product_ids,user_type, product_data=product_data)
        return JsonResponse({'price': result_data})
        
def orderDelete(request, slug):
    try:
        orderdel=OrderManagement.objects.get(slug=slug)
        orderdel.delete()
        messages.success(request,'Delete successfully Done!!')
        return redirect("orderlist")
    except:
        messages.success(request,'Something Went Wrong!!')
        return redirect("orderlist")


def orderEdit(request,slug):
    try:
        template_name = "admin/Order_Management/order_edit.html"
        order_edit=OrderManagement.objects.get(slug=slug)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        seven_days = datetime.date.today() + datetime.timedelta(days=7)
        company=PropertyManagerMember.objects.filter(is_verified ="1")        
        selected_product_ids = []
        selected_product_categories = []
        selected_product_quantity=[]
        for i in order_edit.product_details:
            selected_product_ids.append(i.get('product_id'))
            selected_product_categories.append(i.get('product_category'))
            selected_product_quantity.append(i.get('product_quantity'))
        offers = OfferManagement.objects.filter(category__name__in=selected_product_categories)
        zip_code=FranchisePinCodes.objects.all()
        user_type = order_edit.user_type
        pin_code = order_edit.pin_code
        product_ids = FranchisePinCodesPrice.objects.filter(user_type=user_type,pin_code=pin_code).values_list('product_id', flat=True)
        products=Product.objects.filter(id__in=product_ids).values('id', 'name')
        if request.method == "POST":

            pin_code=request.POST.get('zip-code')
            product_id=request.POST.getlist('products[]')
            offer_id=request.POST.get('offer')
            delivery_date=request.POST.get('delivery-date')
            return_date=request.POST.get('return-date')
            actual=request.POST.get('actual')
            effective=request.POST.get('effective')
            address=request.POST.get('address')
            gate=request.POST.get('gate')
            company_id=request.POST.get('user-company')
            door_code=request.POST.get('door_code')
            reservation_number=request.POST.get('reservation_number')
            subdivision=request.POST.get('subdivision')
            notes=request.POST.get('notes')
            product_quantity_data = json.loads(request.POST.get('product_quantity_data'))
            check_product_quantity=list(product_quantity_data.values())
            product_price=ProductPrice(user_type,pin_code,product_id,delivery_date,return_date)
            product_data=Product.objects.filter(id__in=product_id)
            product_category=Product.objects.filter(id__in=product_id).values_list('category_id')
            for qty in check_product_quantity:
                if Product.objects.filter(id__in=product_id,quantity__lte=qty):
                    messages.error(request,'Quantity Not Available please add minimum quantity')
                    return redirect("/admin/order-edit/" + str(slug))
            if offer_id:
                offer_discount=OfferManagement.objects.get(code=offer_id)
            product_detail = []
            data = []
            for j,i in enumerate(product_data):
                if product_price[j].get('zero_seven_days'):
                    price = product_price[j].get('zero_seven_days') 
                    
                elif product_price[j].get('sale_price'):
                    price = product_price[j].get('sale_price')
                
                elif product_price[j].get('zero_seven_days_wholesale'):
                    price = product_price[j].get('zero_seven_days_wholesale')

                data.append({
                    "product_id": i.id,
                    "product_name":i.name,
                    "product_category":i.category.name,
                    "price": price,
                    "product_return":i.is_return,
                    "product_quantity": product_quantity_data.get(str(i.id))
                })
            if offer_id != None:
                order_edit.product_details=data
                order_edit.pin_code=pin_code
                order_edit.delivery=delivery_date
                order_edit.order_return=return_date
                order_edit.actual_price=actual
                order_edit.discount_price=effective
                order_edit.offer_id=offer_discount.id
                order_edit.Address=address
                order_edit.gate=gate 
                order_edit.company_id=company_id
                order_edit.subdivision=subdivision
                order_edit.reservationnumber=reservation_number
                order_edit.doorcode=door_code 
                order_edit.notes=notes
                order_edit.save()
            else:
                order_edit.product_details=data
                order_edit.pin_code=pin_code
                order_edit.delivery=delivery_date
                order_edit.order_return=return_date
                order_edit.actual_price=actual
                order_edit.discount_price=effective
                order_edit.offer_id=""
                order_edit.Address=address
                order_edit.company_id=company_id
                order_edit.gate=gate 
                order_edit.subdivision=subdivision
                order_edit.reservationnumber=reservation_number
                order_edit.doorcode=door_code 
                order_edit.notes=notes
                order_edit.save()
            user=User.objects.get(id=order_edit.user_id)
            subject = " Welcome to   Honest Sherpa world"
            message = f"Hi {user.first_name} {user.last_name}, Thank you for  Order the product  on Honest Sherpa . Your order id is {order_edit.order_id} and Your paymemt status is Pending "
            recipient_list = [user.email]
            sendMail(subject, message,recipient_list)
            messages.success(request,'Order Successfully Update')
            return redirect('orderlist')
        context={'orderedit':order_edit, 
        'zip_code':zip_code, 
        "products":products, 
        'selected_product_ids': selected_product_ids, 
        'offers': offers,
        "selected_product_quantity":selected_product_quantity,
        "tomorrow":tomorrow,"seven_days":seven_days,"company":company
        }
        return render(request, template_name, context)
    except:
        messages.error(request,'Something Went Wrong!!')
        return redirect('orderlist')


def order_filter_ajax(request):
    sort_list=[]
    if request.method == "POST":
        user_value=request.POST.get('user_type')
        
        order_queryset = OrderManagement.objects.all()
        queryset=Q()
        if user_value == "high":
            sort_price = "-discount_price"
        elif user_value == "low":
            sort_price = "discount_price"
        else:
            sort_price = "-id"
        if user_value == "vacationer" or user_value == "homeowner" or user_value == "propertymanager":
            queryset |= Q(user_type=user_value)
        filter_data=order_queryset.filter(queryset).order_by(f"{sort_price}")
    
        return render(request,'admin/Order_Management/order_filter_listing.html',{'filter_data':filter_data})
            
    return JsonResponse(
                {
                    "status": "success",
                    "message": "Details Submitted Successfully !!!!",
                    # "data":data,           
                },
                status=200,
        )
        



