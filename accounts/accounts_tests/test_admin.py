from django.test import TestCase, Client
from django.contrib.auth import authenticate
from django.urls import reverse

from accounts.admin import UserProfileAdmin
from accounts.models import Account


class UserProfileAdminTest(TestCase):

    def setUp(self):
        self.adminuser = Account.objects.create_superuser(first_name='aman', last_name='aman', email='aman@test.test', 
                    username='aman', phone_number='61111111', password='aman')
    
    def test_user_profile_admin_view(self):
        c = Client()
        response = c.get('/securelogin/accounts/userprofile/')
        self.assertEqual(response.status_code, 302)
        loggedinuser = authenticate(phone_number=self.adminuser.phone_number, password='aman')
        c.login(phone_number=loggedinuser.phone_number, password='aman')
        response = c.get('/securelogin/accounts/userprofile/')
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('admin:accounts_userprofile_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select user profile to change')

        