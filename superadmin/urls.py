"""honest_sherpa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls import handler400, handler403, handler404, handler500

handler404 = "superadmin.views.handler404"

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", views.login, name="logins"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("subadmin/", views.subadmin, name="subadmin"),
    path("add_subadmin/", views.add_subadmin, name="add_subadmin"),
    path("edit_subadmin/<slug>", views.edit_subadmin, name="edit_subadmin"),
    path("delete_subadmin/<int:id>", views.delete_subadmin, name="delete_subadmin"),
    path("customer-view/", views.customer_view, name="customer_view"),
    path("details/<slug>", views.details, name="details"),
    path("user_detail_status/<slug>", views.user_detail_status, name="user_detail_status"),
    path("delete_address/<int:id>", views.delete_address, name="delete_address"),
    path("user_address_delete/<int:id>", views.user_address_delete, name="user_address_delete"),
    path("addaddress/<slug>", views.addaddress, name="addaddress"),
    path("fetch_address/", views. fetch_address, name=" fetch_address"),
    path("edit_address/", views.edit_address, name="edit_address"),
    path("UserActionAjax/", views.UserActionAjax, name="UserActionAjax"),
    path("UserFilterAjax/", views.UserFilterAjax, name="UserFilterAjax"),
    path("UserShowHideAjax/", views.UserShowHideAjax, name="UserShowHideAjax"),
    # path("UserShowHideAjax2/", views.UserShowHideAjax2, name="UserShowHideAjax2"),
    path("whole_sale_status/<slug>", views.whole_sale_status, name="whole_sale_status"),
    path("propertymanager_negotiable_status/<slug>", 
            views.propertymanager_negotiable_status, 
                    name="propertymanager_negotiable_status"),
    path("negotiable_price_ajax/", 
            views.negotiable_price_ajax, 
                    name="negotiable_price_ajax"),



    
    path(
        "customer-registration/",
        views.customer_registration,
        name="customer_registration",
    ),
    
    path("customer_edit/<slug>/", views.customer_edit, name="customer_edit"),
    path(
        "customer_view_detail/<slug>/",
        views.customer_view_detail,
        name="customer_view_detail",
    ),
    path("customer_delete/<int:id>/", views.customer_delete, name="customer_delete"),
    path("add_superadmin/", views.add_superadmin, name="add_superadmin"),
    path("superadmin/", views.superadmin, name="superadmin"),
    path("edit_superadmin/<slug>/", views.edit_superadmin, name="edit_superadmin"),
    path(
        "superadmin_delete/<int:id>/", views.superadmin_delete, name="superadmin_delete"
    ),
    path("homeowner/", views.homeowner, name="homeowner"),
    path("add_homeowner/", views.add_homeowner, name="add_homeowner"),
    path("edit_homeowner/<slug>/", views.edit_homeowner, name="edit_homeowner"),
    path(
        "homeowner_view_detail/<slug>/",
        views.homeowner_view_detail,
        name="homeowner_view_detail",
    ),
    path("homeowner_delete/<int:id>/", views.homeowner_delete, name="homeowner_delete"),
    path("propertymanager/", views.propertymanager, name="propertymanager"),
    path("add_propertymanager/", views.add_propertymanager, name="add_propertymanager"),
    path(
        "edit_propertymanager/<slug>/",
        views.edit_propertymanager,
        name="edit_propertymanager",
    ),
    path(
        "propertymanager_view_detail/<slug>/",
        views.propertymanager_view_detail,
        name="propertymanager_view_detail",
    ),
    path(
        "propertymanager_delete/<int:id>/",
        views.propertymanager_delete,
        name="propertymanager_delete",
    ),
    path("franchise/", views.franchise, name="franchise"),
    path(
        "franchise_verificatoin_admin/",
        views.franchise_verificatoin_admin,
        name="franchise_verificatoin_admin",
    ),
    path(
        "property_manager_verificatoin_admin/",
        views.property_manager_verificatoin_admin,
        name="property_manager_verificatoin_admin",
    ),
    path(
        "vacationer_verificatoin_admin/",
        views.vacationer_verificatoin_admin,
        name="vacationer_verificatoin_admin",
    ),
    path(
        "homeowner_verificatoin_admin/",
        views.homeowner_verificatoin_admin,
        name="homeowner_verificatoin_admin",
    ),
    path("add_franchise/", views.add_franchise, name="add_franchise"),
    path("edit_franchise/<slug>", views.edit_franchise, name="edit_franchise"),
    path(
        "franchise_view_detail/<slug>/",
        views.franchise_view_detail,
        name="franchise_view_detail",
    ),
    path("franchise_delete/<int:id>", views.franchise_delete, name="franchise_delete"),
    path("globalsetting/", views.globalsetting, name="globalsetting"),
    path("globalsetting_add/", views.globalsetting_add, name="globalsetting_add"),
    path(
        "globalsetting_edit/<slug>", views.globalsetting_edit, name="globalsetting_edit"
    ),
    path(
        "globalsetting_view_detail/<slug>/",
        views.globalsetting_view_detail,
        name="globalsetting_view_detail",
    ),
    path(
        "globalsetting_delete/<int:id>",
        views.globalsetting_delete,
        name="globalsetting_delete",
    ),
    path("testimonial/", views.testimonial, name="testimonial"),
    path("testimonial_add/", views.testimonial_add, name="testimonial_add"),
    path("testimonial_edit/<slug>", views.testimonial_edit, name="testimonial_edit"),
    path(
        "testimonial_view_detail/<slug>/",
        views.testimonial_view_detail,
        name="testimonial_view_detail",
    ),
    path(
        "testimonial_delete/<int:id>",
        views.testimonial_delete,
        name="testimonial_delete",
    ),
    path("emailtemplate/", views.emailtemplate, name="emailtemplate"),
    path("emailtemplate_add/", views.emailtemplate_add, name="emailtemplate_add"),
    path(
        "emailtemplate_edit/<slug>", views.emailtemplate_edit, name="emailtemplate_edit"
    ),
    path(
        "emailtemplate_view_detail/<slug>/",
        views.emailtemplate_view_detail,
        name="emailtemplate_view_detail",
    ),
    path(
        "emailtemplate_delete/<int:id>",
        views.emailtemplate_delete,
        name="emailtemplate_delete",
    ),
    path("pending_list/", views.pending_list, name="pending_list"),
    path("pending_list_add/", views.pending_list_add, name="pending_list_add"),
    path(
        "pending_list_reply/<slug>", views.pending_list_reply, name="pending_list_reply"
    ),
    path("reslove_list/", views.reslove_list, name="reslove_list"),
    path(
        "reslove_list_delete/<int:id>",
        views.reslove_list_delete,
        name="reslove_list_delete",
    ),
    # Admin profile url:
    path("view-profile/<slug>", views.view_profile, name="view_profile"),
    path("change-password/<slug>", views.change_password, name="change_password"),
    # Product Management:
    path("category/", views.category, name="category"),
    path("add-category/", views.add_category, name="add_category"),
    path("edit-category/<slug>", views.edit_category, name="edit_category"),
    path("delete-category/<int:id>", views.delete_category, name="delete_category"),
    path("view-category/<slug>", views.view_category, name="view_category"),
    path("subcategory/", views.subcategory, name="subcategory"),
    path("add-subcategory/", views.add_subcategory, name="add_subcategory"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<slug>", views.edit_product, name="edit_product"),
    path("edit-product-price/<str:slug>", views.EditProductPrice, name="edit_product_price"),
    path("pin-code-ajax/", views.pin_code_ajax, name="pin_code_ajax"),


    path("delete_product/<int:id>", views.delete_product, name="delete_product"),
    path("product/", views.product, name="product"),
    path("view-product/<slug>", views.view_product, name="view_product"),
    path("product_status_change_detail/<slug>", views.product_status_change_detail, name="product_status_change_detail"),
    # Superadmin and Subadmin forgot password step:
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-otp/<slug>", views.forgot_otp, name="forgot_otp"),
    path(
        "forgot-password-form/<slug>",
        views.forgot_password_form,
        name="forgot_password_form",
    ),
    path("resend_otp/<slug>", views.resend_otp, name="resend_otp"),
    # Offer Management :
    path("offer/", views.offer, name="offer"),
    path("offer-add/", views.offer_add, name="offer_add"),
    path("offer-edit/<slug>", views.offer_edit, name="offer_edit"),
    path("view-offer/<slug>", views.view_offer, name="view_offer"),
    path("offer-delete/<int:id>", views.offer_delete, name="offer_delete"),
    # Option Management :
    path("option/", views.option, name="option"),
    path("add_option/", views.add_option, name="add_option"),
    path("edit_option/<slug>", views.edit_option, name="edit_option"),
    path("option_delete/<int:id>", views.option_delete, name="option_delete"),
    path("option_value/", views.option_value, name="option_value"),
    path("add_option_value/", views.add_option_value, name="add_option_value"),
    path(
        "edit_option_value/<int:id>", views.edit_option_value, name="edit_option_value"
    ),
    path(
        "delete_option_value/<int:id>",
        views.delete_option_value,
        name="delete_option_value",
    ),
    path(
        "fetch_product_option",
        views.fetch_product_option,
        name="fetch_product_option",
    ),
    path(
        "fetch_product_option_value",
        views.fetch_product_option_value,
        name="fetch_product_option_value",
    ),
    path("Faq/", views.Faq, name="Faq"),
    path("add_faq/", views.add_faq, name="add_faq"),
    path("edit-faq/<slug>", views.edit_faq, name="edit_faq"),
    path("view-faq/<slug>", views.view_faq, name="view_faq"),
    path("delete-faq/<int:id>", views.delete_faq, name="delete_faq"),
    path("blog/", views.blog, name="blog"),
    path("add_blog/", views.add_blog, name="add_blog"),
    path("edit-blog/<slug>", views.edit_blog, name="edit_blog"),
    path("view-blog/<slug>", views.view_blog, name="view_blog"),
    path("delete-blog/<int:id>", views.delete_blog, name="delete_blog"),
    path("subcategory/", views.subcategory, name="subcategory"),
    path("add_subcategory/", views.add_subcategory, name="add_subcategory"),
    path("edit-subcategory/<slug>", views.edit_subcategory, name="edit_subcategory"),
    path("view-subcategory/<slug>", views.view_subcategory, name="view_subcategory"),
    path(
        "delete-subcategory/<int:id>",
        views.delete_subcategory,
        name="delete_subcategory",
    ),
    path("select_subcategory/", views.select_subcategory, name="select_subcategory"),
    path("report/", views.report, name="report"),
    path("generate-pdf/<str:id>/", views.generate_pdf, name="generate_pdf"),
    path("user_data_pdf/<slug>/", views.user_data_pdf, name="user_data_pdf"),
    path("notification/", views.notification, name="notification"),
    path(
        "delete-notification/<slug>",
        views.delete_notification,
        name="delete_notification",
    ),
    path("email_notification/", views.email_notification, name="email_notification"),
    path(
        "request-products-list/",
        views.request_products_list,
        name="request_products_list",
    ),
    path("add_pages/<slug>", views.add_pages, name="add_pages"),
    path("pages/", views.cms_page, name="cms_page"),
    # path("add-coupon/", views.add_coupon, name="add_coupon"),
    path("product_ajax/", views.product_ajax, name="product_ajax"),

    
    path("edit_product_ajax/", views.edit_product_ajax, name="edit_product_ajax"),
    path("test/", views.test, name="test"),
    path("appbanner/", views.appbanner, name="appbanner"),
    path("edit-appbanner/<slug>/", views.edit_appbanner, name="edit_appbanner"),
    path("about-us/", views.aboutUs, name="aboutUs"),
    # path("distance/", views.Distance, name="distance"),
    # path("edit-distance/<slug>", views.EditDistance, name="EditDistance"),


    # ----------------Order Management ------------------------------------
    path("order-list/", views.orderlist, name="orderlist"),
    path("Add-Order/", views.AddOrder, name="Add_Order"),
    path("select_User/", views.select_User, name="select_User"),
    path("select_product/", views.select_product, name="select_product"),
    path("select_pincode/", views.select_pincode, name="select_pincode"),
    path("change_date/", views.change_date, name="change_date"),
    path("select_offer/", views.select_offer, name="select_offer"),
    path("order-view/<str:slug>/", views.orderView, name="order_view"),
    path("change-actual-price/", views.changeActualPrice, name="change_actual_price"),
    path("order-delete/<str:slug>", views.orderDelete, name="order_delete"),
    path("order-edit/<str:slug>", views.orderEdit, name="order_edit"),
    path("order_filter_ajax/", views.order_filter_ajax, name="order_filter_ajax"),




    
    
    path("add/company/", views.add_company, name="add_company"),
    path("company_listing/", views.company_listing, name="company_listing"),
    path("company/edit/<slug>", views.company_edit, name="company_edit"),
    path("company_delete/<int:id>", views.company_delete, name="company_delete"),
    path("company/view/<slug>", views.company_view, name="company_view"),
    # import export sku code
    path("excel_skucode/", views.excel_skucode, name="excel_skucode"),
    
    path("import_excel/", views.import_excel, name="import_excel"),
]
