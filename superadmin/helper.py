from bdb import effective
from email import message
import math
import random
from unittest import result
from django.conf import settings
from io import BytesIO
from django.core.mail import send_mail
from django.template.loader import get_template
from importlib_metadata import re
from superadmin.models import *
import xhtml2pdf.pisa as pisa
from django.contrib import messages

# from xhtml2pdf import pisa
from django.http import HttpResponse
from django.db.models import Sum



def generateOTP():
    # Declare a digits variable
    # which stored all digits
    digits = "1234567890"
    Otp = ""
    # length of password can be changed
    # by changing value in range
    for i in range(4):
        Otp += digits[math.floor(random.random() * 10)]
    return Otp


def generatePassword():
    # Declare a digits variable
    # which stored all digits
    digits = "Abcdefgh@#()1234567890"
    Password = ""
    # length of password can be changed
    # by changing value in range
    for i in range(8):
        Password += digits[math.floor(random.random() * 10)]
    return Password


def sendMail(subject, message, recipient):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient,
    )
    return None


def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None


def generate_sku_code(request, product_name):
    digits = random.randint(1000, 9999)
    SKU_CODE = product_name.upper()[0:3] + str(digits)
    # generate_sku_code(request, product_name)
    return SKU_CODE


def calculate_order_price(zip_code,product,user_type, **kwargs):
    data = {}
    products=Product.objects.filter(id__in=product).values_list("is_return" , flat=True)
    pin_price_code=FranchisePinCodesPrice.objects.filter(pin_code=zip_code,product_id__in=product,
    user_type=user_type)
    result=[]
    product_data = kwargs['product_data']
   
    if 'offer' in kwargs :
        offer_discount=kwargs['offer']
        offer_price=OfferManagement.objects.get(code=offer_discount)
        pin_code_price=FranchisePinCodesPrice.objects.filter(pin_code=zip_code,product_id__in=product,
        user_type=user_type,product__category_id=offer_price.category_id)
        if 'days_diffrence' in kwargs:
            days_diffrence_default=7
            days_diffrence=kwargs['days_diffrence']
            if days_diffrence >= days_diffrence_default:
                for i in products:
                    if user_type=="vacationer" or user_type == "homeowner":
                        if i == True: 
                            data = pin_code_price.values('product_id', 'zero_seven_days',"greaterthan_seven",'sale_price')
                        else:
                            data = pin_code_price.values('product_id', 'zero_seven_days','sale_price',"greaterthan_seven")
                    else:
                        if i == True: 
                            data = pin_code_price.values('product_id', 'zero_seven_days_wholesale', 'greaterthan_seven_wholesale','sale_price')
                        else:
                            data = pin_code_price.values('product_id', 'zero_seven_days_wholesale', 'greaterthan_seven_wholesale','sale_price')
                days_count=days_diffrence-days_diffrence_default
                for i in data:
                    quantity = product_data.get(str(i.get('product_id')), 1)
                    if i.get('zero_seven_days') != None:
                        result.append(float(i.get('zero_seven_days'))*float(quantity))
                    if i.get('greaterthan_seven') != None:
                        if days_count != 0:
                            greaterthan_sevens=float(i.get('greaterthan_seven'))*float(days_count+1)*float(quantity)
                            result.append(greaterthan_sevens)
                        else:
                            greaterthan_sevens=float(i.get('greaterthan_seven'))*float(quantity)
                            result.append(greaterthan_sevens)
                    if i.get('zero_seven_days_wholesale') != None:
                        result.append(float(i.get('zero_seven_days_wholesale'))*float(quantity))
                    if i.get('greaterthan_seven_wholesale') != None:
                        if days_count != 0:
                            greaterthan_seven_wholesales=float(i.get('greaterthan_seven_wholesale'))*float(days_count+1)*float(quantity)
                            result.append(greaterthan_seven_wholesales)
                        else:
                            greaterthan_seven_wholesales=float(i.get('greaterthan_seven_wholesale'))*float(quantity)
                            result.append(greaterthan_seven_wholesales)
                    if i.get('sale_price') != None:
                        result.append(float(i.get('sale_price'))*float(quantity))                              
                discount_price=float(offer_price.offer_discount)
                effective_price=float(sum(result))*(discount_price/100)
                
                return round(effective_price,2)
            else: 
                for i in products:
                    if user_type=="vacationer" or user_type == "homeowner":
                        if i == True: 
                            data = pin_code_price.values('product_id','zero_seven_days','sale_price')
                        else:
                            data = pin_code_price.values('product_id','zero_seven_days','sale_price')
                    else:
                        if i == True: 
                            data = pin_code_price.values('product_id','zero_seven_days_wholesale')
                        else:
                            data = pin_code_price.values('product_id','zero_seven_days_wholesale','sale_price')
                for  i in data:
                    quantity = product_data.get(str(i.get('product_id')), 1)
                  
                    if i.get('zero_seven_days') != None:
                        result.append(float(i.get('zero_seven_days'))*float(quantity))
                    if i.get('zero_seven_days_wholesale') != None:
                        result.append(float(i.get('zero_seven_days_wholesale'))*float(quantity))
                    if i.get('sale_price') != None:
                        result.append(float(i.get('sale_price'))*float(quantity))
              
                discount_price=float(offer_price.offer_discount)
                effective_price=float(sum(result))*(discount_price/100)
                
                return round(effective_price,2)
        else: 
            for i in products:
                if user_type=="vacationer" or user_type == "homeowner":    
                    if i == True: 
                        data = pin_code_price.values('product_id', 'zero_seven_days', 'sale_price')
                    else:
                        data = pin_code_price.values('product_id', 'zero_seven_days','sale_price')
                else:
                    if i == True: 
                        data = pin_code_price.values('product_id', 'zero_seven_days_wholesale', 'sale_price')
                    else:
                        data = pin_code_price.values('product_id', 'zero_seven_days_wholesale','sale_price')
            for  i in data:
                quantity = product_data.get(str(i.get('product_id')), 1)
                if i.get('zero_seven_days') != None:
                    result.append(float(i.get('zero_seven_days'))*(quantity))
                if i.get('zero_seven_days_wholesale') != None:
                    result.append(float(i.get('zero_seven_days_wholesale'))*(quantity))
                if i.get('sale_price') != None:
                    result.append(float(i.get('sale_price'))*(quantity))
            discount_price=float(offer_price.offer_discount)
            effective_price=(sum(result))*(discount_price/100)
            return round(effective_price,2)
    else:
        if 'days_diffrence' in kwargs:
            days_diffrence_default=7
            days_diffrence=kwargs['days_diffrence']
           
            if days_diffrence >= days_diffrence_default:
                for i in products:
                    if user_type=="vacationer" or user_type == "homeowner":
                        if i == True: 
                            data = pin_price_code.values('product_id', 'zero_seven_days',"greaterthan_seven",'sale_price')
                        else:
                            data = pin_price_code.values('product_id', 'zero_seven_days','sale_price',"greaterthan_seven")
                    else:
                        if i == True: 
                            data = pin_price_code.values('product_id','zero_seven_days_wholesale', 'greaterthan_seven_wholesale','sale_price')
                        else:
                            data = pin_price_code.values('product_id','zero_seven_days_wholesale', 'greaterthan_seven_wholesale','sale_price')
                days_count=days_diffrence-days_diffrence_default  
             
                for  i in data:
                    quantity = product_data.get(str(i.get('product_id')), 1)
                    if i.get('zero_seven_days') != None:
                        result.append(float(i.get('zero_seven_days'))*float(quantity))
                    if i.get('greaterthan_seven') != None:
                        if days_count != 0:
                          
                            greaterthan_sevens=float(i.get('greaterthan_seven'))*float(days_count+1)*float(quantity)
                            result.append(greaterthan_sevens)
                        else:
                            print('2334354656547')
                            greaterthan_sevens=float(i.get('greaterthan_seven'))*float(quantity)
                            result.append(greaterthan_sevens)
                    if i.get('zero_seven_days_wholesale') != None:
                        result.append(float(i.get('zero_seven_days_wholesale'))*float(quantity))
                    if i.get('greaterthan_seven_wholesale') != None:
                        if days_count != 0:
                            greaterthan_seven_wholesales=float(i.get('greaterthan_seven_wholesale'))*float(days_count)*float(quantity)
                            result.append(greaterthan_seven_wholesales)
                        else:
                            greaterthan_seven_wholesales=float(i.get('greaterthan_seven_wholesale'))*float(quantity)
                            result.append(greaterthan_seven_wholesales)
                    if i.get('sale_price') != None:
                        result.append(float(i.get('sale_price'))*float(quantity))
                print(result,'88898989898')
                return round(sum(result),2)
        else:
            for i in products:
                if user_type=="vacationer" or user_type == "homeowner":
                    if i == True: 
                        data = pin_price_code.values('zero_seven_days', 'sale_price', 'product_id')
                    else:
                        data = pin_price_code.values('zero_seven_days','sale_price', 'product_id')
                else:
                    if i == True: 
                        data = pin_price_code.values('zero_seven_days_wholesale', 'sale_price', 'product_id')
                    else:
                        data = pin_price_code.values('zero_seven_days_wholesale','sale_price', 'product_id')
            for  i in data:
                quantity = product_data.get(str(i.get('product_id')), 1)
                if i.get('zero_seven_days'):
                    result.append(float(i.get('zero_seven_days'))*float(quantity))
                if i.get('zero_seven_days_wholesale'):
                    result.append(float(i.get('zero_seven_days_wholesale'))*float(quantity))
                if i.get('sale_price'):
                    result.append(float(i.get('sale_price'))*float(quantity))
            return round(sum(result),2)


def createorderid():
    if OrderManagement.objects.all().exists():
            obj = OrderManagement.objects.last()
            a=obj.order_id
            b=int(a[3:len(a)])+1
            order_id=str("ord")+str(b)
    else:
        order_id='ord1'
    return order_id

def ProductPrice(user_type,pin_code,product_id,delivery_date,return_date):
    pincodeprice=FranchisePinCodesPrice.objects.filter(user_type=user_type,pin_code=pin_code,product_id__in=product_id)
    delivery_convert_date = datetime.datetime.strptime(delivery_date, '%Y-%m-%d').date()
    return_convert_date = datetime.datetime.strptime(return_date, '%Y-%m-%d').date()
    days_diffrence=return_convert_date-delivery_convert_date
    days_diffrence_count=int('{}'.format(days_diffrence.days))
    days_diffrence_default=7
    data={}
    reuslt=[]
    Sums=[]
    if days_diffrence_count>=days_diffrence_default:
        days_count=days_diffrence_count-days_diffrence_default
        if user_type=="vacationer" or user_type == "homeowner":
            data=pincodeprice.values('zero_seven_days','greaterthan_seven','sale_price')
        else:
            data=pincodeprice.values('zero_seven_days_wholesale', 'greaterthan_seven_wholesale', 'sale_price')       
        for i in data:
            if i.get('zero_seven_days') != None:
                    Sums.append(float(i.get('zero_seven_days')))
            if i.get('greaterthan_seven') != None:
                    if days_count == 0:
                        a=float(i.get('greaterthan_seven'))*float(days_count)
                        Sums.append(a)
                    else:
                        a=float(i.get('greaterthan_seven'))*float(days_count+1)
                        Sums.append(a)
            if i.get('zero_seven_days_wholesale') != None:
                Sums.append(float(i.get('zero_seven_days_wholesale')))
                if i.get('greaterthan_seven_wholesale') != None:
                    if days_count == 0:
                        a=float(i.get('greaterthan_seven_wholesale'))*float(days_count)
                        Sums.append(a)
                    else:
                        a=float(i.get('greaterthan_seven_wholesale'))*float(days_count+1)
                        Sums.append(a)
        reuslt.append(dict(zero_seven_days=sum(Sums)))
        for j in data:                
            if j.get('sale_price') != None:
                reuslt.append(dict(sale_price=j.get('sale_price'))) 
        return reuslt
    else:
        if user_type=="vacationer" or user_type == "homeowner":
            data=pincodeprice.values('zero_seven_days','sale_price')
        else:
            data=pincodeprice.values('zero_seven_days_wholesale','sale_price')
        for i in data:
            if i.get('zero_seven_days') != None:
                reuslt.append(dict(zero_seven_days=i.get('zero_seven_days')))
            if i.get('zero_seven_days_wholesale') != None:
                reuslt.append(dict(zero_seven_days_wholesale=i.get('zero_seven_days_wholesale')))
            if i.get('sale_price') != None:
                reuslt.append(dict(sale_price=i.get('sale_price'))) 
        return reuslt
