import tempfile
import pytest

from django.test import TestCase, Client
from accounts.models import Account, BillingAddress, Driver, UserProfile, Vendor, VerificationCode


@pytest.fixture
def user(db):
    new_user = Account.objects.create(
                            first_name='aman', last_name='aman', username='aman999999',
                            email='aman999999@aman.aman', phone_number='61999999', is_active=True, is_staff=True
                        )
    new_user.set_password('aman')
    new_user.save()
    return new_user

@pytest.fixture
def vendor(db, user):
    return Vendor.objects.create(user=user, official_name='sargajak')


class AccountsModelsTest(TestCase):
    def create_user(self, first_name='aman', last_name='aman', username='aman', 
                email='aman@aman.aman', phone_number='61111111'):
        return Account.objects.create(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number='61111111'
                        )
                    
    def create_user_without_phone_number(self, first_name='aman', last_name='aman', username='aman', 
                email='aman@aman.aman', phone_number=''):
        return Account.objects.create_user(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number=phone_number
                        )
    
    def test_account_creation(self):
        new_user = self.create_user()
        self.assertTrue(isinstance(new_user, Account))
        self.assertEqual('aman@aman.aman', new_user.email)
        self.assertEqual(new_user.first_name, 'aman')
        self.assertEqual(new_user.__str__(), 'aman@aman.aman')
        self.assertEqual(new_user.full_name(), 'aman aman')
        
    def test_account_creation_without_phone_number(self):
        with self.assertRaises(ValueError):
            self.create_user_without_phone_number()
    
    def test_userprofile_create(self):
        image = tempfile.NamedTemporaryFile(suffix='.jpg').name
        user = self.create_user()
        userprofile = UserProfile()
        userprofile.user = user 
        userprofile.profile_picture = image
        userprofile.save()
        self.assertTrue(isinstance(userprofile, UserProfile))
        self.assertIn('jpg',userprofile.profile_picture_url())
        self.assertEqual(userprofile.__str__(), user.first_name)
        userprofile.profile_picture = None
        self.assertEqual(userprofile.profile_picture_url(), None)
        self.assertIn('jpg',userprofile.image_name(userprofile))
    
    def test_verificationcode_create(self):
        user = self.create_user()
        vcode = VerificationCode()
        vcode.user = user
        vcode.code = 2222
        vcode.save()
        self.assertTrue(isinstance(vcode, VerificationCode))
        self.assertEqual(vcode.__str__(), '2222')
    
    def test_billing_address_create(self):
        user = self.create_user()
        billingaddress = BillingAddress()
        billingaddress.user = user
        billingaddress.phone_extra = '65555555'
        billingaddress.address_line_1 = 'some address'
        billingaddress.address_line_2 = 'some address 2'
        billingaddress.city = 'Asgabat'
        billingaddress.state = 'Ahal'
        billingaddress.country = 'Turkmenistan'
        billingaddress.save()
        self.assertTrue(isinstance(billingaddress, BillingAddress))
        self.assertEqual(billingaddress.full_address(), 'some address / some address 2')
        self.assertEqual(billingaddress.__str__(), 'some address / Asgabat')
    
    def test_vendor_create(self):
        user = self.create_user()
        vendor = Vendor.objects.create(user=user, official_name='sargajak')
        self.assertTrue(isinstance(vendor, Vendor))
        self.assertEqual(vendor.__str__(), 'sargajak')
        
        c = Client()
        response = c.get(vendor.get_vendor_products_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Store')
        self.assertContains(response, 'Items found')
    
    def test_driver_create(self):
        user = self.create_user()
        vendor = Vendor.objects.create(user=user, official_name='sargajak')
        driver = Driver.objects.create(vendor=vendor, first_name='arslan', last_name='agamuradov', car_brand='toyota',
                car_model='corolla', car_year='2016', car_plate='1320', mobile='61070747')
        self.assertTrue(isinstance(driver, Driver))
        self.assertEqual(driver.__str__(), 'arslan agamuradov corolla 1320 61070747')
        


        
    
