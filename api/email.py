from django.conf import settings
from django.core.mail import send_mail, EmailMessage
import random
import threading
from threading import Thread
from datetime import date, timedelta
from datetime import datetime
import time

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        msg = EmailMessage(self.subject, self.html_content, settings.EMAIL_HOST_USER, self.recipient_list)
        msg.send()

def sendOTP(user):
    # email = EmailTemplate.objects.get(name='Verify Email OTP')
    otp = random.randint(1000, 9999)
    subject = 'Email Verification OTP'
    # data = ''
    # replace_data = data.format(first_name=user.first_name, otp=otp)
    # clear = re.compile('<.*?>') 
    message = f'Welcome {user.first_name}\n\nYour OTP is: {otp}\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()
    user.OTP = otp
    user.save()

def changePasswordOTP(user):
    # email = EmailTemplate.objects.get(name='Verify Email OTP')
    otp = random.randint(1000, 9999)
    subject = 'Change Password OTP verification'
    # data = ''
    # replace_data = data.format(first_name=user.first_name, otp=otp)
    # clear = re.compile('<.*?>') 
    message = f'Hello {user.first_name}\n\nYour OTP is: {otp}\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()
    user.OTP = otp
    user.otp_sent_time = datetime.now()
    user.save()

def changePassword(user):
    # email = EmailTemplate.objects.get(name='Verify Email OTP')
    subject = 'Password changed Successfully'
    # data = ''
    # replace_data = data.format(first_name=user.first_name, otp=otp)
    # clear = re.compile('<.*?>') 
    message = f'Hello {user.first_name}\n\nYour Password has successfully changed.\nIf you did not recognised this. Please Change your credentails ASAP.\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()

def sendMobileOTP(user):
    # email = EmailTemplate.objects.get(name='Verify Email OTP')
    otp = random.randint(1000, 9999)
    subject = 'Change Password'
    # data = ''
    # replace_data = data.format(first_name=user.first_name, otp=otp)
    # clear = re.compile('<.*?>') 
    message = f'Hello {user.first_name}\n\nYour Login OTP is: {otp}\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()
    user.OTP = otp
    user.otp_sent_time = datetime.now()
    user.save()

def sendTicket(user):
    # email = EmailTemplate.objects.get(name='Verify Email OTP')
    subject = f'Your Ticket Number: {user.ticket}'
    # data = ''
    # replace_data = data.format(first_name=user.first_name, otp=otp)
    # clear = re.compile('<.*?>') 
    message = f'Hello {user.name}\n\nYour Ticket Number is: {user.ticket}\n\nCreated at: {user.created_at}\n\nSubject is: {user.question}\n\nWe will try to response soon. Please connected with us.\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()

def sendAlert(user):
    # email = EmailTemplate.objects.get(name='Your Password has been changed!')
    subject = 'Your Password has been changed!'
    # data = email.editor
    message = f'Hello {user.first_name}\n\nYour Password is successfully Reset.\nPassword updated on {str(datetime.now())[:19]}\nPlease connected with us.\n\nThanks & Regards\nHonest Sherpa'
    EmailThread(subject, message, [user.email]).start()
