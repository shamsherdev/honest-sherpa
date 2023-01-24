from django.test import TestCase
from django.contrib.auth import get_user_model
# from superadmin.models import User
from faker import Faker

# Create your tests here.
User = get_user_model()
faker = Faker()
class UserRegister(TestCase):
    def setUp(self):
        for _ in range(10):
            user_a = User(email=faker.unique.email(), first_name=faker.first_name())
            user_a.is_verified = False
            user_a.set_password('Test@123')
            user_a.save()

    # def test_userExists(self):
    #     # user_test = User.objects.all().count()
    #     user_test = User.objects.filter(email='test101@getnada.com', is_verified=False).exists()
    #     print(user_test, '----------------')
    #     self.assertEqual(user_test, True)

    # def test_mobile(self):
    #     user_mobile = User.objects.get(email='test102@getnada.com')
    #     user_mobile.mobile = '9876543210'

    def test_users(self):
        # users = []
        user_data = User.objects.values_list('id', 'first_name', 'email')
        # for i in user_data:
        #     users.append(i.email)
        print(user_data)

    # def test_userExiste(self):
    #     user = User.objects.filter(email__iexats='jjones@example.net')