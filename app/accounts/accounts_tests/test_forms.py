import imp
from django.test import TestCase, Client
from django.urls import reverse

from .. import forms


class RegistrationModelFormTest(TestCase):
    
    def setUp(self):
        self.data = {
            'first_name':'aman', 'last_name':'aman', 'phone_number':'64444444', 'email':'amana@gmail.com', 
            'password':'aman', 'confirm_password':'aman'
        }
        self.data_invalid_phone_number = {

            'first_name':'aman', 'last_name':'aman', 'phone_number':'66444445', 'email':'amans@gmail.com', 
            'password':'aman', 'confirm_password':'aman'
        }
        self.data_invalid_password = {

            'first_name':'aman', 'last_name':'aman', 'phone_number':'66444443', 'email':'amand@gmail.com', 
            'password':'aman', 'confirm_password':'aman2'
        }

        self.data_empty_password = {

            'first_name':'aman', 'last_name':'aman', 'phone_number':'66444442', 'email':'amanf@gmail.com', 
            'password':'', 'confirm_password':''
        }
    
    def test_adding_new_user(self):
        c = Client()
        response = c.post(reverse('registration'), data=self.data)
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertContains(response, 'We sent a confirmation code')
    
    def test_adding_invalid_phone_number(self):
        c = Client()
        response = c.post(reverse('registration'), data=self.data_invalid_phone_number)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Phone number is not valid')
        self.assertTemplateUsed(response, 'accounts/registration.html')
    
    def test_adding_invalid_password(self):
        c = Client()
        response = c.post(reverse('registration'), data=self.data_invalid_password)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match!')
        self.assertTemplateUsed(response, 'accounts/registration.html')

    def test_adding_empty_password(self):
        c = Client()
        response = c.post(reverse('registration'), data=self.data_empty_password)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')
        self.assertContains(response, 'Passwords cannot be empty')