from pyexpat import model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ImageField
from . import choices
import uuid
from .manager import CustomUserManager
import datetime
from random import randint
from jsonfield import JSONField


# Create your models here.


class BaseTable(models.Model):
    sr = models.BooleanField(default=False)
    name = models.BooleanField(default=False)
    created = models.BooleanField(default=False)
    action = models.BooleanField(default=False)

    class Meta:
        abstract = True


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


class User(AbstractUser):
    roll = models.CharField(
        max_length=50,
        choices=choices.USER_TYPE,
    )
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    profile_pic = models.ImageField(null=True, blank=True, upload_to="user/%Y/%m/%d/")
    mobile_number = models.CharField(
        max_length=50,
    )
    city = models.CharField(
        max_length=50,
    )
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    OTP = models.CharField(max_length=10)
    otp_count = models.CharField(max_length=10, default=0, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    license_number = models.IntegerField(null=True, blank=True)
    id_number = models.IntegerField(null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    notification_settings = models.BooleanField(default=True)
    location_settings = models.BooleanField(default=True)
    is_verified = models.BooleanField(default="0")
    otp_sent_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    company_address = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_set_up_status = models.BooleanField(default=False)
    time_zone = models.CharField(max_length=50, null=True, blank=True)
    identification_number = models.CharField(max_length=50, null=True, blank=True)
    manager = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    reason = models.CharField(max_length=50, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    property_manager_type = models.CharField(max_length=50, null=True, blank=True)
    company_status = models.BooleanField(default=False)
    wholesale_price_status = models.BooleanField(default=False)
    propertymanager_negotiable = models.BooleanField(default=False)
    objects = CustomUserManager()

    class Meta:
        permissions = (("can_sidebar", "Can Sidebar"),)

    def __str__(self):
        return self.email


class Dashboard(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_dashboard", "Can Sidebar dashboard"),
            ("can_view_dashboard", "Can view dashboard"),
        )


class aboutuspage(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_about", "Can Sidebar about"),
            ("can_view_about", "Can view about"),
        )


class Reports(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_Sidebar_reports", "Can Sidebar reports"),
            ("can_view_reports", "Can view reports"),
            ("can_download_reports", "Can download reports"),
        )


class Cms(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_Sidebar_cms", "Can Sidebar cms"),
            ("can_change_cms", "Can change cms"),
            ("can_view_cms", "Can view cms"),
        )


class product_option(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_Sidebar_product_option", "Can Sidebar product_option"),
            ("can_change_product_option", "Can change product_option"),
            ("can_view_product_option", "Can view product_option"),
            ("can_add_product_option", "Can add product_option"),
            ("can_delete_product_option", "Can delete product_option"),
        )


class Orders(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_Sidebar_orders", "Can Sidebar orders"),
            ("can_view_orders", "Can view orders"),
        )


class Enquiry(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_enquiry", "Can Sidebar enquiry"),
            ("can_view_enquiry", "Can view enquiry"),
        )


class email(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_email", "Can Sidebar email"),
            ("can_change_email", "Can change email"),
            ("can_view_email", "Can view email"),
        )


class appbanners(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_appbanners", "Can Sidebar appbanners"),
            ("can_change_appbanners", "Can change appbanners"),
            ("can_view_appbanners", "Can view appbanners"),
        )


class globalsettings(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_globalsetting", "Can Sidebar globalsetting"),
            ("can_change_globalsetting", "Can change globalsetting"),
            ("can_view_globalsetting", "Can view globalsetting"),
        )


class requestproducts(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (
            ("can_sidebar_requestproducts", "Can Sidebar requestproducts"),
            ("can_change_requestproducts", "Can change requestproducts"),
            ("can_view_requestproducts", "Can view requestproducts"),
        )


# class Subadmin(models.Model):
#     class Meta:
#         # No database table creation or deletion  \
#         # operations will be performed for this model.

#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_subadmin", "Can Sidebar subadmin"),
#             ("add_subadmin", "can add subadmin"),
#             ("change_subadmin", "can change change"),
#             ("delete_subadmin", "can delete subadmin"),
#             ("view_subadmin", "can view subadmin"),
#         )


# class Superadmin(models.Model):
#     class Meta:
#         # No database table creation or deletion  \
#         # operations will be performed for this model.

#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_superadmin", "Can Sidebar superadmin"),
#             ("add_superadmin", "can add superadmin"),
#             ("change_superadmin", "can change superadmin"),
#             ("delete_superadmin", "can delete superadmin"),
#             ("view_superadmin", "can view superadmin"),
#         )


# class Customer(models.Model):
#     class Meta:
#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_customer", "Can Sidebar customer"),
#             ("add_customer", "can add customer"),
#             ("change_customer", "can change customer"),
#             ("delete_customer", "can delete customer"),
#             ("view_customer", "can view customer"),
#         )


# class Homeowners(models.Model):
#     class Meta:
#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_homeowners", "Can Sidebar homeowners"),
#             ("add_homeowners", "can add homeowners"),
#             ("change_homeowners", "can change homeowners"),
#             ("delete_homeowners", "can delete homeowners"),
#             ("view_homeowners", "can view homeowners"),
#         )


# class Propertymanager(models.Model):
#     class Meta:
#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_propertymanager", "Can Sidebar propertymanager"),
#             ("add_propertymanager", "can add propertymanager"),
#             ("change_propertymanager", "can change propertymanager"),
#             ("delete_propertymanager", "can delete propertymanager"),
#             ("view_propertymanager", "can view propertymanager"),
#         )


# class Franchise(models.Model):
#     class Meta:
#         default_permissions = ()
#         permissions = (
#             ("can_sidebar_franchise", "Can Sidebar franchise"),
#             ("add_franchise", "can add franchise"),
#             ("change_franchise", "can change franchise"),
#             ("delete_franchise", "can delete franchise"),
#             ("view_franchise", "can view franchise"),
#         )


class GlobalSetting(models.Model):
    text = models.TextField(null=True, blank=True)
    global_image = models.ImageField(
        upload_to="globalsetting/%Y/%m/%d/", null=True, blank=True
    )
    logo_image = models.ImageField(
        upload_to="globalsetting/%Y/%m/%d/", null=True, blank=True
    )
    global_url_insta = models.URLField(null=True, blank=True)
    global_url_facebook = models.URLField(null=True, blank=True)
    global_url_twitter = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_globalsetting", "Can Sidebar GlobalSetting"),)


class Testimonial(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    desgination = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    testimonial_image = models.ImageField(
        upload_to="testimonial/%Y/%m/%d/", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_testimonial", "Can Sidebar Testimonial"),)


class EmailTemplate(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_emailtemplate", "Can Sidebar EmailTemplate"),)


class Contactus(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(unique=False)
    question = models.CharField(max_length=250, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_pending = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    ticket = models.CharField(max_length=250, null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_contactus", "Can Sidebar Contactus"),)

    def save(self, *args, **kwargs):
        self.ticket = random_with_N_digits(12)
        super(Contactus, self).save(*args, **kwargs)


class ProductCategory(models.Model):
    name = models.CharField(max_length=250)
    category_image = models.ImageField(
        upload_to="category/%Y/%m/%d/", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_productcategory", "Can Sidebar ProductCategory"),)


class ProductSubCategory(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    subcategory_image = models.ImageField(
        upload_to="subcategory/%Y/%m/%d/", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (
            ("can_sidebar_productsubcategory", "Can Sidebar ProductSubCategory"),
        )


class OfferManagement(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    offer_name = models.CharField(max_length=250, null=True, blank=True)
    offer_image = models.ImageField(upload_to="offer/%Y/%m/%d/", null=True, blank=True)
    offer_terms_condition = models.TextField(null=True, blank=True)
    offer_validity = models.DateField(null=True, blank=True)
    offer_discount = models.CharField(max_length=10,null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True, unique=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_apply = models.BooleanField(default=False)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_Sidebar_offermanagement", "Can Sidebar OfferManagement"),)

class Options(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_options", "Can Sidebar options"),)


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE,null=True, blank=True)
    option = models.ForeignKey(Options, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="productImage/", null=True)
    image1 = models.ImageField(upload_to="productImage/", null=True)
    image2 = models.ImageField(upload_to="productImage/", null=True)
    image3 = models.ImageField(upload_to="productImage/", null=True)
    image4 = models.ImageField(upload_to="productImage/", null=True)
    # oneday_price = models.IntegerField(null=True, blank=True)
    # week_price = models.IntegerField(null=True, blank=True)
    # month_price = models.IntegerField(null=True, blank=True)
    # two_week_price = models.IntegerField(null=True, blank=True)
   
    quantity = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=250)
    latitude = models.CharField(max_length=250)
    longitude = models.CharField(max_length=250)
    # sku_code = models.CharField(max_length=250, null=True, blank=True)
    avaliable = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_feature = models.BooleanField(default=False)
   
    created_at = models.DateField(auto_now_add=True)
    average_rating=models.IntegerField(null=True,blank=True)
    purchased_date = models.DateField(null=True,blank=True)
    purchased_price = models.CharField(max_length=50,null=True,blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_product", "Can Sidebar Product"),)


class ProductSkuCodes(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku_code = models.CharField(max_length=250, unique=True)
    status = models.BooleanField(default=False)

class ProductFranchiseMember(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

class Options_value(models.Model):
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE
    )
    option = models.ForeignKey(Options, on_delete=models.CASCADE)
    option_name = models.CharField(max_length=250, null=True, blank=True)
    option_value = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    option_slug = models.CharField(max_length=50)

    class Meta:
        permissions = (("can_sidebar_options_value", "Can Sidebar options_value"),)


class ProductOptions(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    option = models.ForeignKey(Options, on_delete=models.CASCADE)
    option_value = models.ForeignKey(Options_value, on_delete=models.CASCADE)
    price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    Productoptions_image = models.ImageField(
        upload_to="Productoptions/%Y/%m/%d/", null=True, blank=True
    )
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_ProductOptions", "Can Sidebar ProductOptions"),)


class FAQ(models.Model):
    question = models.CharField(max_length=250, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_FAQ", "Can Sidebar FAQ"),)


class Blog(models.Model):
    blog_title = models.CharField(max_length=250, null=True, blank=True)
    blog_video = models.FileField(upload_to="Blog/", null=True, blank=True)
    blog_image = models.ImageField(upload_to="Blog/%Y/%m/%d/", null=True, blank=True)
    blog_description = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_Blog", "Can Sidebar Blog"),)


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_receiver",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=30, choices=choices.NOTIFICATION_TYPE, null=True, blank=True
    )
    notification = models.CharField(max_length=255, null=True, blank=True)
    notification_id = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class RequestProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_id",
        null=True,
        blank=True,
    )

    quantity = models.CharField(
        max_length=50,
    )
    created = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_requestproduct", "Can Sidebar request product"),)


class ApprovedProductByAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        RequestProduct,
        on_delete=models.CASCADE,
        related_name="approved_product_id",
        null=True,
        blank=True,
    )

    quantity = models.CharField(
        max_length=50,
    )
    created = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class AppSlider(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="slider/", null=True, blank=True)
    video = models.FileField(upload_to="slider/", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class pages(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    text1 = models.TextField()
    text2 = models.TextField()
    text3 = models.TextField()
    content = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="pages/")
    soft_del_status = models.BooleanField(default=False)
    is_deleted = models.BooleanField(null=True)


class ProductDistance(models.Model):
    distance = models.IntegerField(null=False, blank=False)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class ProductFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_favourite = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class AddToCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    offer = models.ForeignKey(OfferManagement, on_delete=models.CASCADE, null=True, blank=True)
    size = models.CharField(max_length=20, default=0)
    quantity = models.CharField(max_length=20, default=1)
    date_diffrence= models.CharField(max_length=20,null=True,blank=True)
    delivery_date = models.DateField(auto_now_add=False, null=True, blank=True)
    return_date = models.DateField(auto_now_add=False, null=True, blank=True)
    product_total_price= models.CharField(max_length=20,null=True,blank=True)
    product_discount=models.CharField(max_length=20,null=True,blank=True)
    total_price = models.CharField(max_length=50,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    price = models.CharField(max_length=250, null=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, null=True, blank=True, on_delete=models.CASCADE
    )
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_Sidebar_coupon", "Can Sidebar coupon"),)


class Contact(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    user_type = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    company_name = models.CharField(max_length=250, null=True, blank=True)
    subject = models.CharField(max_length=250, null=True, blank=True)
    message = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    answer = models.TextField(null=True, blank=True)
    is_pending = models.BooleanField(default=True)
    replied_time = models.DateField(null=True, blank=True)  
    ticket = models.CharField(max_length=250, null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    class Meta:
        permissions = (("can_sidebar_contact", "Can Sidebar contact"),)


class FranchisePinCodes(models.Model):
    pin_code = models.CharField(null=True, blank=True, max_length=10,unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # daily_price = models.CharField(null=True, blank=True, max_length=10)
    # weekly_price = models.CharField(null=True, blank=True, max_length=10)
    # yearly_price = models.CharField(null=True, blank=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)


class FranchisePinCodesPrice(models.Model):
    pin_code = models.CharField(null=True, blank=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # zip_code = models.ForeignKey(FranchisePinCodes, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(null=True, blank=True, max_length=10)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    zero_seven_days = models.CharField(null=True, blank=True, max_length=10)
    greaterthan_seven = models.CharField(null=True, blank=True, max_length=10)
    zero_seven_days_wholesale = models.CharField(null=True, blank=True, max_length=10)
    greaterthan_seven_wholesale = models.CharField(null=True, blank=True, max_length=10)
    sale_price = models.CharField(null=True, blank=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    # yearly_price = models.CharField(null=True, blank=True, max_length=10)
    # two_weekly_price = models.CharField(null=True, blank=True, max_length=10)
    # monthly_price = models.CharField(null=True, blank=True, max_length=10)

    # twoweekly_wholesale_price = models.CharField(null=True, blank=True, max_length=10)
    # monthly_wholesale_price = models.CharField(null=True, blank=True, max_length=10)
    # yearly_wholesale_price = models.CharField(null=True, blank=True, max_length=10)


class AppBanner(models.Model):
    video = models.FileField(
        upload_to="deploy/appbanner/videos/%Y/%m/%d/", null=True, verbose_name=""
    )
    image = models.ImageField(
        upload_to="deploy/appbanner/images/%Y/%m/%d/",
        null=True,
    )
    title = models.CharField(null=True, blank=True, max_length=10)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

    content = models.CharField(null=True, blank=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (("can_sidebar_appbanner", "Can Sidebar app banner"),)


class AboutUs(models.Model):
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    description1 = models.CharField(max_length=250, null=True, blank=True)
    description2 = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(
        upload_to="deploy/aboutus/images/%Y/%m/%d/",
        null=True,
    )
    description3 = models.CharField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class UserMultipleAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    zip_code = models.CharField(max_length=250, null=True, blank=True)
    latitude = models.CharField(max_length=50,null=True, blank=True)
    longitude = models.CharField(max_length=50,null=True, blank=True)
    location=models.CharField(max_length=250,null=True,blank=True)
    address_defaults=models.BooleanField(default=False)
    address_apply=models.BooleanField(default=False)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class UserDataHideShow(BaseTable):
    email = models.BooleanField(default=False)
    role = models.BooleanField(default=False)


class PropertyManagerMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    companyname = models.CharField(max_length=250, null=True, blank=True)
    companyemail = models.CharField(max_length=250, null=True, blank=True)
    companycontact = models.CharField(max_length=250, null=True, blank=True)
    companyaddress = models.CharField(max_length=250, null=True, blank=True)

    companyzip_code = models.CharField(
        max_length=250, unique=True, null=True, blank=True
    )
    is_verified = models.BooleanField(default="0")
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class SelectProertyManagerCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(
        PropertyManagerMember, on_delete=models.CASCADE, null=True, blank=True
    )
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class WholeSalePriceData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pincode_wholesale_price = models.ForeignKey(
        FranchisePinCodesPrice, on_delete=models.CASCADE, null=True, blank=True
    )
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class ProductReviewRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    rating=models.IntegerField(null=True,blank=True)
    review=models.TextField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
      
class OrderDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    user_address = models.ForeignKey(UserMultipleAddress, on_delete=models.CASCADE, null=True, blank=True)

    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class OfferUsed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Offer = models.ForeignKey(OfferManagement, on_delete=models.CASCADE)
    is_used=models.BooleanField(default=True)
    # order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)


class OrderManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pin_code = models.CharField(null=True, blank=True, max_length=10)
    offer = models.ForeignKey(OfferManagement, on_delete=models.CASCADE, null=True, blank=True)
    addtocart = models.ForeignKey(AddToCart, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    transaction_id=models.CharField(max_length=50, unique=True, null=True, blank=True)
    order_created = models.DateField(auto_now_add=True, null=True, blank=True)
    delivery = models.DateField(null=True, blank=True)
    order_return = models.DateField(null=True, blank=True)
    order_created_by = models.CharField(max_length=50, null=True, blank=True)
    actual_price=models.CharField(max_length=50, null=True, blank=True)
    discount_price=models.CharField(max_length=50, null=True, blank=True)
    Address = models.CharField(max_length=250, null=True, blank=True)
    payment_status=models.BooleanField(default=False)
    product_details = JSONField()
    order_status=models.CharField(max_length=50,
        choices=choices.Order_Status)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)


class Order_Delivery(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(OrderManagement, on_delete=models.CASCADE, null=True, blank=True)
    order_status= models.CharField(
        max_length=50,
        choices=choices.Order_Status,
    )
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    slug = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
