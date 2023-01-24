from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", views.login, name="logins"),
    path("logout/", views.logouts, name="logouts"),
    path("dashboard/", views.dashboard, name="dashboards"),
    path("product-list/", views.product_list, name="product_list"),
    path("product-detail/<slug>", views.product_detail, name="product_detail"),
    path(
        "franchise_forgot_password/",
        views.franchise_forgot_password,
        name="franchise_forgot_password",
    ),
    path("otp/<slug>", views.otp, name="otp"),
    path("resend_otp/<slug>", views.resend_otp, name="resend_otp"),
    path("reset_password/<slug>", views.reset_password, name="reset_password"),
    path("view-profile/<slug>", views.view_profile, name="view_profile"),
    path("change-password/<slug>", views.change_password, name="change_password"),
    path("request_products/", views.request_products, name="request_products"),
    path("approved_request_products_by_admin/", views.approved_request_products_by_admin, name="approved_request_products_by_admin"),
    path("my_product_list/", views.my_product_list, name="my_product_list"),
    path("order-list/", views.orderList, name="order_list"),
    
]
