# from django.conf.urls import urls
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("location_pincode/", views.location_pincode, name="location_pincode"),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("profile/setup/<slug>", views.profile_setup, name="profile_setup"),
    path(
        "verify/sign-up/otp/<slug>", views.verify_signup_otp, name="verify_signup_otp"
    ),
    path(
        "sign/up/resend/otp/<slug>", views.sign_up_resend_otp, name="sign_up_resend_otp"
    ),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("forgot/password/", views.forgot_password, name="forgot_password"),
    path(
        "forgot/password/otp/<slug>",
        views.verify_forgot_password_otp,
        name="verify_forgot_password_otp",
    ),
    path(
        "reset/password/<slug>",
        views.reset_password_form,
        name="reset_password_form",
    ),
    path(
        "resend/otp/<slug>",
        views.resend_otp,
        name="resend_otp",
    ),
    path(
        "my/profile/<slug>",
        views.my_profile,
        name="my_profile",
    ),
    path(
        "update_profile_pic/<slug>",
        views.update_profile_pic,
        name="update_profile_pic",
    ),
    path(
        "change/password/<slug>",
        views.change_password,
        name="change_password",
    ),
    path(
        "view/all/category",
        views.category,
        name="category",
    ),
    path(
        "category/list/<slug>",
        views.category_list,
        name="category_list",
    ),

    path(
        "view/all/product/listing/",
        views.view_all_product_listing,
        name="view_all_product_listing",
    ),


    path(
        "featured/all/product/listing",
        views.featured_all_product_listing,
        name="featured_all_product_listing",
    ),
    path(
        "product/details/<slug>",
        views.ProductDetails,
        name="ProductDetails",
    ),
    path(
        "product/favourite/",
        views.productFavourite,
        name="productFavourite",
    ),
    path(
        "add/to/cart/",
        views.add_to_cart,
        name="add_to_cart",
    ),
    path(
        "add/to/cart/ajax/",
        views.add_to_cart_ajax,
        name="add_to_cart_ajax",
    ),
    
    path(
        "cart/items",
        views.cart_items,
        name="cart_items",
    ),
    path(
        "clear/cart",
        views.clear_cart,
        name="clear_cart",
    ),
    path(
        "delete/cart/items/<int:id>",
        views.delete_cart_items,
        name="delete_cart_items",
    ),
    path(
        "my/wishlist",
        views.wishlist,
        name="wishlist",
    ),
    path(
        "delete/wishlist/<int:id>",
        views.delete_wishlist,
        name="delete_wishlist",
    ),
    path(
        "contact/us",
        views.contact_us,
        name="contact_us",
    ),
    path(
        "search/result/",
        views.search_result,
        name="search_result",
    ),
    path(
        "sub_category_ajax_dayanamic",
        views.sub_category_ajax_dayanamic,
        name="sub_category_ajax_dayanamic",
    ),
    path(
        "select_user/",
        views.select_user,
        name="select_user",
    ),
    path(
        "about/",
        views.about,
        name="about",
    ),
    path(
        "select_property_company/<slug>",
        views.select_property_company,
        name="select_property_company",
    ),
    path(
        "blog/detail/<slug>",
        views.blog_detail,
        name="blog_detail",
    ),
    path(
        "blog/list/",
        views.blog_list,
        name="blog_list",
    ),
    path(
        "review_rating/",
        views.review_rating,
        name="review_rating",
    ),
      path(
        "my_address/",
        views.my_address,
        name="my_address",
    ),
     path(
        "Add/New/Address/",
        views.AddNewAddress,
        name="AddNewAddress",
    ),
     path(
        "change_default_address/<int:id>",
        views.change_default_address,
        name="change_default_address",
    ),
    path(
        "Delete_Address/<int:id>",
        views.Delete_Address,
        name="Delete_Address",
    ),
     path(
        "Edit/address/",
        views.Edit_address,
        name="Edit_address",
    ),
     path(
        "fetch_address/",
        views.fetch_address,
        name="fetch_address",
    ),
     path(
        "apply_address/<int:id>",
        views.apply_address,
        name="apply_address",
    ),
     path(
        "change_delivery_date/",
        views.change_delivery_date,
        name="change_delivery_date",
    ),
    path(
        "apply/offer/list/",
        views.apply_offer_list,
        name="apply_offer_list",
    ),
    path(
        "offer-apply/<int:id>/",
        views.offerApply,
        name="offer_apply",
    ),
    path(
        "remove-offer/<int:id>/",
        views.removeOffer,
        name="remove_offer",
    ),
    path("order-create/",views.orderCreate,name="order_create"),
    path("my-order/",views.myOrder,name="my_order"),
    path("order-details/<str:slug>/",views.orderDetails,name="order_details"),
    path("order-cancel/<str:slug>/",views.orderCancel,name="order_cancel"),


]


