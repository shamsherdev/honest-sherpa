from django.http import request
from superadmin.models import *
from rest_framework import serializers
from haversine import haversine, Unit
from math import radians, cos, sin, asin, sqrt
import json
from .utils import *

# def haversine(lon1, lat1, lon2, lat2):
#     lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#     # haversine formula


class RegitserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "roll"]

        extra_kwargs = {"password": {"write_only": True}}

    # if 'roll' == 'homenowner':
    #     def create(self, validated_data):
    #         user = User(email = validated_data['email'], roll = validated_data['roll'], mobile_number = validated_data['mobile_number'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], profile_pic=validated_data['profile_pic'])
    #         user.set_password(validated_data['password'])
    #         user.save()
    #         return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class MobileLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()


class MobileLoginOTPVerifySerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    otp = serializers.CharField()


class ChangePasswordMobileOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    otp = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()


class ChangePasswordVerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class ChangePasswordMobileSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "profile_pic",
            "first_name",
            "last_name",
            "mobile_number",
            "state",
            "city",
            "address",
            "zip_code",
        ]
        extra_kwargs = {"profile_pic": {"required": False}}


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options_value
        fields = ["id", "option_name", "option_value", "is_active"]


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "roll",
            "profile_pic",
            "first_name",
            "last_name",
            "mobile_number",
            "state",
            "city",
            "zip_code",
            "address",
            "notification_settings",
            "location_settings",
            'profile_set_up_status',
            "is_verified",
            "is_active",
            "date_joined",
            "last_login",
            "latitude",
            "longitude",
        ]


class ProductSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    # size = serializers.SerializerMethodField()
    favourite_product = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            "id",
            "name",
            "image",
            "image1",
            "image2",
            "image3",
            "image4",
            "oneday_price",
            "week_price",
            "month_price",
            "options",
            "quantity",
            "description",
            "avaliable",
            "is_return",
            "is_feature",
            "category",
            "subcategory",
            "favourite_product",
        ]
        depth = 1

    def get_options(self, instance):
        if instance.option:
            get_data = Options_value.objects.filter(option_id=instance.option.id)
            serializer = ProductOptionSerializer(get_data, many=True)
            return serializer.data
        return None

    def get_favourite_product(self, instance):
        user_id = self.context["user_id"]
        products = ProductFavourite.objects.filter(
            user_id=user_id, product_id=instance.id
        )
        if products:
            return True
        else:
            return False

    # def get_size(self, instance):
    #     if instance.option.name == "Size" and instance.option.is_active == 1:
    #         get_data = Options_value.objects.filter(option_id=instance.option.id)
    #         serializer = ProductOptionSerializer(get_data, many=True)
    #         return serializer.data
    #     return None


class ProductHomeSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    # size = serializers.SerializerMethodField()
    # favourite_product = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            "id",
            "name",
            "image",
            "image1",
            "image2",
            "image3",
            "image4",
            "oneday_price",
            "week_price",
            "month_price",
            "options",
            "quantity",
            "description",
            "avaliable",
            "is_return",
            "is_feature",
            "category",
            "subcategory",
        ]
        depth = 1

    def get_options(self, instance):
        if instance.option:
            get_data = Options_value.objects.filter(option_id=instance.option.id)
            serializer = ProductOptionSerializer(get_data, many=True)
            return serializer.data
        return None

    # def get_size(self, instance):
    #     if instance.option.name == "Size" and instance.option.is_active == 1:
    #         get_data = Options_value.objects.filter(option_id=instance.option.id)
    #         serializer = ProductOptionSerializer(get_data, many=True)
    #         return serializer.data
    #     return None


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"
        depth = 1


class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = "__all__"
        depth = 1


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactus
        fields = "__all__"
        # depth = 1


class AllSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSlider
        fields = "__all__"
        # depth = 1


class AllBannerSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    featured_product = serializers.SerializerMethodField()

    class Meta:
        model = AppBanner
        fields = [
            "id",
            "image",
            "category",
            "products",
            "featured_product",
        ]
        # depth = 1

    def get_category(self, instance):
        category = ProductCategory.objects.all()[:5]
        serializer = ProductCategorySerializer(category, many=True)
        return serializer.data

    def get_products(self, instance):
        try:
            latitude1 = self.context["latitude"]
            longitude1 = self.context["longitude"]
            productdistance = ProductDistance.objects.get(id=1)
            select_distance = productdistance.distance
            obj_list = list()
            products = Product.objects.all()[:5]
            for i in products:
                first = (float(latitude1), float(longitude1))
                second = (float(i.latitude), float(i.longitude))
                distance = get_distance(latitude1, longitude1, i.latitude, i.longitude)
                if float(select_distance) > float(distance):
                    obj_list.append(i)
                serializer = ProductHomeSerializer(obj_list, many=True)
                return serializer.data
        except:
            return "Please Provide latitude longitude"

    def get_featured_product(self, instance):
        products = Product.objects.filter(is_feature=True)[:5]
        serializer = ProductHomeSerializer(products, many=True)
        return serializer.data


class HomeAppSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = '__all__'
        fields = [
            "id",
            "name",
            "image",
            "image1",
            "image2",
            "image3",
            "image4",
            "oneday_price",
            "week_price",
            "month_price",
            "color",
            "size",
            "quantity",
            "description",
            "avaliable",
            "is_return",
            "is_feature",
            "category",
            "subcategory",
        ]

    def get_color(self, instance):
        if instance.option.name == "color" and instance.option.is_active == 1:
            get_data = Options_value.objects.filter(option_id=instance.option.id)
            serializer = ProductOptionSerializer(get_data, many=True)
            return serializer.data
        return None

    def get_size(self, instance):
        if instance.option.name == "Size" and instance.option.is_active == 1:
            get_data = Options_value.objects.filter(option_id=instance.option.id)
            serializer = ProductOptionSerializer(get_data, many=True)
            return serializer.data
        return None


class ProductFavouriteSerializer(serializers.ModelSerializer):
    # favourite_product = serializers.SerializerMethodField()
    class Meta:
        model = ProductFavourite
        fields = ["id", "is_favourite", "product", "created"]
        depth = 1

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep["product"] = ProductSerializer(instance.product).data
    #     return rep

class AppBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppBanner
        fields = "__all__"