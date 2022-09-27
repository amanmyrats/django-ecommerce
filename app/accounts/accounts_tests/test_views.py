import imp
from multiprocessing import context
from re import A
from urllib import response
from django.http import HttpRequest
from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.sessions.backends.db import SessionStore

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order


from .. import views, forms, models
from store.models import Product, Variation


class AccountPageTests(TestCase):

    def setUp(self):
        self.new_user =  models.Account.objects.create(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number='61111111', is_active=True, is_staff=True
                        )
        self.new_user.set_password('aman')
        self.new_user.save()
        self.new_user2 =  models.Account.objects.create(
                            first_name='aman', last_name='aman', username='aman2',
                            email='aman@gmail.com', phone_number='61555555', is_active=True, is_staff=True
                        )
        self.new_user2.set_password('aman')
        self.new_user2.save()
        self.new_user_not_staff =  models.Account.objects.create(
                            first_name='aman', last_name='aman', username='amannotstaff',
                            email='aman@notstaff.com', phone_number='61222222', is_active=True, is_staff=False
                        )
        self.new_user_not_staff.set_password('aman')
        self.new_user_not_staff.save()
        self.c = Client()

        self.new_user_inactive =  models.Account.objects.create(
                            first_name='aman', last_name='aman', username='aman3',
                            email='aman@test.com', phone_number='61666666', is_staff=True
                        )
        self.new_user_inactive.set_password('aman')
        self.new_user_inactive.save()
        self.c = Client()

        self.vendor = models.Vendor.objects.create(
            user=self.new_user,
            official_name='sargajak'
        )

        

    # def tearDown(self):
    #     return super().tearDown()

    def test_registration_view(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')
        self.assertContains(response, 'Sign up')
        self.assertNotContains(response, '404')

        response = self.client.get('/en/accounts/registration/')
        self.assertEqual(response.status_code, 200)

        register_response = self.client.post(reverse('registration'), {
            'first_name':'aman', 'last_name':'aman', 'email':'aman@gmail.gmail', 
            'phone_number':'65666666', 'password':'aman', 'confirm_password':'aman'
        })
        self.assertEqual(register_response.status_code, 302)
    
    def test_update_phone_number_1(self):
        c = Client()
        # Since there is no phone number in url parameter, 
        # It will redirect to login page, So status_code must be 302
        response_without_phone_number = c.get(reverse('update_phone_number'))
        self.assertEqual(response_without_phone_number.status_code, 302)
        next = c.get(response_without_phone_number.url)
        self.assertContains(next, 'Sign in')

    def test_update_phone_number_2(self):
        c = Client()
        # When someone writes phone number manually in url parameters
        response_with_phone_number_that_does_not_exist = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'63333333', 'updated_phone_number':'65666667'})
        self.assertEqual(response_with_phone_number_that_does_not_exist.status_code, 302)
        response_with_phone_number_that_does_not_exist = c.get(response_with_phone_number_that_does_not_exist.url)
        self.assertEqual(response_with_phone_number_that_does_not_exist.status_code, 200)
        self.assertContains(response_with_phone_number_that_does_not_exist, 'There is no user with this phone number')
    
    def test_update_phone_number_3(self):
        c = Client()
        # Since there is current_phone_number in GET request, 
        # it will open page successfully, status_code must be 200
        response_with_phone_number = c.get(reverse('update_phone_number'), {'current_phone_number':'61111111'})
        self.assertEqual(response_with_phone_number.status_code, 200)

    def test_update_phone_number_4(self):
        c = Client()
        # New phone number, that is requested to be replaced with current one,
        # is already used by another user, so it will redirect to edit_profile
        # Anonymous User
        response_with_phone_number = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'61111111', 'updated_phone_number':'61555555'})
        self.assertEqual(response_with_phone_number.status_code, 302)
        response_with_phone_number = c.get(response_with_phone_number.url)
        self.assertContains(response_with_phone_number, 'Sign in')

    def test_update_phone_number_5(self):
        c = Client()
        # New phone number, that is requested to be replaced with current one,
        # is already used by another user, so it will redirect to edit_profile
        # Logged in User
        user = authenticate(phone_number=self.new_user.phone_number, password='aman')
        c.login(phone_number=user.phone_number, password='aman')
        response_with_phone_number = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'61111111', 'updated_phone_number':'61555555'})
        self.assertEqual(response_with_phone_number.status_code, 302)
        response_with_phone_number = c.get(response_with_phone_number.url)
        self.assertContains(response_with_phone_number, 'Edit Your Profile')

    def test_update_phone_number_6(self):
        c = Client()
        user = authenticate(phone_number=self.new_user.phone_number, password='aman')
        c.login(phone_number=user.phone_number, password='aman')
        # Current phone number and request's user's phone number are not same
        response_with_phone_number = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'61555555', 'updated_phone_number':'65000000'})
        self.assertEqual(response_with_phone_number.status_code, 302)
        next = self.client.get(response_with_phone_number.url)
        self.assertEqual(next.status_code, 200)
        self.assertContains(next, 'Sign in')
    
    def test_update_phone_number_7(self):
        c = Client()
        # Current phone number is in use
        response_with_phone_number = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'61555555', 'updated_phone_number':'65000000'})
        self.assertEqual(response_with_phone_number.status_code, 302)
        next = self.client.get(response_with_phone_number.url)
        self.assertEqual(next.status_code, 200)
        self.assertContains(next, 'Sign in')
        
    def test_update_phone_number_8(self):
        c = Client()
        user = authenticate(phone_number=self.new_user.phone_number, password='aman')
        c.login(phone_number=user.phone_number, password='aman')
        # Logged in user changes his/her number with proper number
        response_with_phone_number = c.post(reverse('update_phone_number'), 
                            {'current_phone_number':'61111111', 'updated_phone_number':'65666666'})
        self.assertEqual(response_with_phone_number.status_code, 302)
        next = self.client.get('/en{}'.format(response_with_phone_number.url))
        self.assertEqual(next.status_code, 200)
        self.assertContains(next, 'verify')



    def test_edit_profile_view(self):
        c = Client()

        # Login required, that is why 404
        response = c.get(reverse('edit_profile'))
        self.assertTrue(response.status_code, 404)
        

        # After login
        user = authenticate(phone_number=self.new_user.phone_number, password='aman')
        c.login(phone_number=user.phone_number, password='aman')
        response = c.get(reverse('edit_profile'))
        self.assertTrue(response.status_code, 200)

        # Second get request
        response = c.get(reverse('edit_profile'))
        self.assertTrue(response.status_code, 200)

        # POST request with invalid form
        response = c.post(reverse('edit_profile'))
        self.assertEqual(response.status_code,302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)

        # POST request with valid form
        response = c.post(reverse('edit_profile'), data={'first_name':'aman', 'last_name':'aman'})
        self.assertEqual(response.status_code,302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your profile has been updated')
    

    def test_login_with_wrong_credentials(self):
        c = Client()
        response = c.post(reverse('login'), data={'phone_number':self.new_user.phone_number, 'password':'wrongpassword'})
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid login credentials')
        self.assertTemplateUsed('accounts/login.html')

        response = c.post(reverse('login'), data={'phone_number':self.new_user_inactive.phone_number, 'password':'aman'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('mobileverification', response.url)
        response = c.get(response.url)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We sent a confirmation code')
    
    def test_login_with_right_credentials(self):
        c = Client()
        response = c.post(reverse('login'), data={'phone_number':self.new_user.phone_number, 'password':'aman'})
        self.assertEqual(response.status_code, 302)
        response = c.post(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are now logged in')
    
    def test_login_with_right_credentials_with_next(self):
        c = Client()
        response = c.post(reverse('login'), data={'phone_number':self.new_user.phone_number, 'password':'aman'})
        self.assertEqual(response.status_code, 302)
        response = c.post(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are now logged in')
    
    def test_login_with_product_in_cart(self):
        c = Client()
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.post(reverse('add_product'), data={'product_name':'jeans', 
                    'description':'beaitiful jeans'})
        response = c.post(reverse('add_product'), data={'product_name':'shoes', 
                    'description':'beaitiful shoes'})
        self.assertTrue(Product.objects.count()==2)
        self.assertTrue(Variation.objects.count()==2)
        
        product_jeans = Product.objects.get(product_name='jeans')
        variation_jeans = Variation.objects.get(product__product_name='jeans')
        variation_jeans.quantity=10
        variation_jeans.save()
        product_shoes = Product.objects.get(product_name='shoes')
        variation_shoes = Variation.objects.get(product__product_name='shoes')
        variation_shoes.quantity = 10
        variation_shoes.save()

        # 1 - Add variation jeans when logged in
        response = c.post(reverse('add_cart', kwargs={'product_id':product_jeans.id}),
                        data={'product_id':product_jeans.id, 'variation_id':variation_jeans.id})

        users_items = CartItem.objects.filter(user=self.new_user)
        self.assertTrue(users_items.count()==1)
        variation_jeans_item = CartItem.objects.get(user=self.new_user, variation=variation_jeans)
        self.assertTrue(variation_jeans_item.quantity==1)

        # 2 - Then logout and add variaton jeans and variation shoes
        # c.logout()
        c.get(reverse('logout'))
        response = c.post(reverse('add_cart', kwargs={'product_id':product_jeans.id}),
                        data={'product_id':product_jeans.id, 'variation_id':variation_jeans.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':product_shoes.id}),
                        data={'product_id':product_shoes.id, 'variation_id':variation_shoes.id})
        
        cart_items = CartItem.objects.filter(user=None)
        self.assertTrue(cart_items.count()==2)
        variation_jeans_item = CartItem.objects.get(variation=variation_jeans, user=None)
        print('variation_jeans_item', variation_jeans_item.quantity)
        self.assertTrue(variation_jeans_item.quantity==1)
        variation_shoes_item = CartItem.objects.get(variation=variation_shoes, user=None)
        print('variation_shoes_item', variation_shoes_item.quantity)
        self.assertTrue(variation_shoes_item.quantity==1)

        # 3 - Then login, two products which were added when I was logged out should be added into my cart.
        response = c.post(reverse('login'), data={'phone_number':self.new_user.phone_number, 'password':'aman'})
        self.assertEqual(response.status_code, 302)
        users_items = CartItem.objects.filter(user=self.new_user)
        self.assertTrue(users_items.count()==2)
        variation_jeans_item = CartItem.objects.get(user=self.new_user, variation=variation_jeans)
        self.assertTrue(variation_jeans_item.quantity==2)
    
    def test_activate_by_phone_number_with_unregistered_user(self):
        c = Client()
        response = c.post(reverse('activate_by_phone_number'), data={
            'phone_number':63999999,
            'mobile_verification_code':2222
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('registration', response.url)
    
    def test_activate_by_phone_number_without_verification_code(self):
        c = Client()
        response = c.post(reverse('activate_by_phone_number'), data={
            'phone_number':self.new_user.phone_number,
            'mobile_verification_code':2222
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('registration', response.url)

    def test_activate_by_phone_number_with_wrong_verification_code(self):
        c = Client()
        models.VerificationCode.objects.create(user=self.new_user, code=2222)
        response = c.post(reverse('activate_by_phone_number'), data={
            'phone_number':self.new_user.phone_number,
            'mobile_verification_code':3333
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('registration', response.url)
    
    def test_activate_by_phone_number_with_correct_verification_code(self):
        c = Client()
        models.VerificationCode.objects.create(user=self.new_user, code=2222)
        response = c.post(reverse('activate_by_phone_number'), data={
            'phone_number':self.new_user.phone_number,
            'mobile_verification_code':2222
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_forgot_password(self):
        c = Client()
        # GET request
        response = c.get(reverse('forgotPassword'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Write your phone number')

        # POST with wrong phone number
        response = c.post(reverse('forgotPassword'), data={'phone_number':64444444})
        self.assertEqual(response.status_code, 302)
        self.assertIn('forgotPassword', response.url)
        response = c.get(response.url)
        self.assertContains(response, 'Account does not exist')

        # POST with correct phone number
        respone = c.post(reverse('forgotPassword'), data={'phone_number':61111111})
        self.assertEqual(response.status_code, 200)

    def test_resetPassword(self):
        c = Client()
        # GET request
        response = c.get(reverse('resetPassword'))
        self.assertEqual(response.status_code, 200)
        
        # POST with unmatching passwords
        response = c.post(reverse('resetPassword'), 
                    data={'phone_number':64444444, 'password':'aman', 'confirm_password':'amanaman'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')

        # POST matching passwords with user that does not exist
        response = c.post(reverse('resetPassword'), 
                    data={'phone_number':64444444, 'password':'aman', 'confirm_password':'aman'})
        self.assertEqual(response.status_code, 404)

        # POST matching passwords with proper user
        response = c.post(reverse('resetPassword'), 
                    data={'phone_number':61111111, 'password':'aman', 'confirm_password':'aman'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)

    def test_resetpassword_validate_by_mobile(self):
        c = Client()
        # GET request
        response = c.get(reverse('resetpassword_validate_by_mobile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('resetPassword', response.url)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)

        # POST with non-user phone number
        response = c.post(reverse('resetpassword_validate_by_mobile'), data={'phone_number':64444444, 'verification_code':2222})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This user does not exist')

        # POST with proper user phone number, but without any verification code in database
        response = c.post(reverse('resetpassword_validate_by_mobile'), data={'phone_number':61111111, 'verification_code':2222})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)

        models.VerificationCode.objects.create(code=2222, user=self.new_user)

        # POST with proper user phone number and with wrong verification code in database
        response = c.post(reverse('resetpassword_validate_by_mobile'), data={'phone_number':self.new_user.phone_number, 'verification_code':3333})
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This code is not matching')

        # POST with proper user phone number and with proper verification code
        models.VerificationCode.objects.create(code=2222, user=self.new_user)
        response = c.post(reverse('resetpassword_validate_by_mobile'), data={'phone_number':self.new_user.phone_number, 'verification_code':2222})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please choose new password')

    def test_change_password(self):
        c = Client()
        # GET request
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.get(reverse('change_password'))
        print('response', response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/change_password.html')

        # POST request wrong current password
        response = c.post(reverse('change_password'), data={
            'current_password':'amana',
            'new_password':'amanaman',
            'confirm_password':'amanaman'
        })
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter valid current password')
        self.assertTemplateUsed('accounts/change_password.html')

        # POST request unmatching password
        response = c.post(reverse('change_password'), data={
            'current_password':'aman',
            'new_password':'amanamana',
            'confirm_password':'amanaman'
        })
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password does not match')
        self.assertTemplateUsed('accounts/change_password.html')

        # POST request proper data
        response = c.post(reverse('change_password'), data={
            'current_password':'aman',
            'new_password':'amanaman',
            'confirm_password':'amanaman'
        })
        self.assertEqual(response.status_code, 302)
        response = c.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password updated successfully')
        self.assertTemplateUsed('accounts/login.html')

    def test_registration(self):
        c = Client()
        response = c.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')
        self.assertTemplateUsed('accounts/registration.html')

        response = c.post(reverse('registration'), data={
            'first_name' : 'aman',
            'last_name' : 'murat',
            'phone_number' : '61999999',
            'email' : 'aman@amannewuser.aman',
            'password' : 'aman',
            'confirm_password' : 'aman',
            'username' : '61999999',
        })
        new_user = models.UserProfile.objects.get(user__email='aman@amannewuser.aman')
        # print('new_user', new_user)
        self.assertIsInstance(new_user, models.UserProfile)
        self.assertEqual(response.status_code, 302)

    def test_my_orders(self):
        c = Client()
        response = c.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/my_orders.html')
    
    def test_order_detail(self):
        c = Client()
        new_order = Order()
        new_order.order_number = 2022222222
        new_order.order_number_vendor = 2022222233
        new_order.order_total = 0
        new_order.slug = 'orderslug'
        new_order.save()
        response = c.get(reverse('order_detail', kwargs={'order_vendor_id':new_order.order_number_vendor}))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.get(reverse('order_detail', kwargs={'order_vendor_id':new_order.order_number_vendor}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/order_detail.html')
        # Logged in user and orders owner is not same
        c.get(reverse('logout'))
        c.login(phone_number=self.new_user_not_staff.phone_number, password='aman')
        response = c.get(reverse('order_detail', kwargs={'order_vendor_id':new_order.order_number_vendor}))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('store/store.html')

    def test_saleslistview(self):
        c = Client()
        response = c.get(reverse('sales'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.get(reverse('sales'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/sales.html')
        response = c.get(reverse('vendor_sales', kwargs={'vendor_slug':'sargajak'}), data={'status':1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/sales.html')

    def test_saledetailview(self):
        c = Client()
        response = c.get(reverse('vendor_sale_detail', kwargs={'vendor_slug':'sargajak', 'order_slug':'someslug'}))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        c.login(phone_number=self.new_user.phone_number, password='aman')
        new_order = Order()
        new_order.order_number = 2022222222
        new_order.order_number_vendor = 2022222233
        new_order.order_total = 0
        new_order.slug = 'orderslug'
        new_order.save()
        response = c.get(reverse('vendor_sale_detail', kwargs={'vendor_slug':self.vendor.slug, 'order_slug':new_order.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('accounts/sales.html')
        # fields = ['order_number_vendor', 'status', 'driver', 'driver_fee']
        # post method with form errors
        response = c.post(reverse('vendor_sale_detail', kwargs={'vendor_slug':self.vendor.slug, 'order_slug':new_order.slug}), \
            data={'status':1, 'driver':'', 'driver_fee':10})
        self.assertEqual(response.status_code, 200)
        # post method with valid form
        response = c.post(reverse('vendor_sale_detail', kwargs={'vendor_slug':self.vendor.slug, 'order_slug':new_order.slug}), \
            data={'order_number_vendor':new_order.order_number_vendor, 'status':1, 'driver':'', 'driver_fee':10})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/sales.html')
        # post method with non-vendor user
        c.login(phone_number=self.new_user2.phone_number, password='aman')
        response = c.post(reverse('vendor_sale_detail', kwargs={'vendor_slug':self.vendor.slug, 'order_slug':new_order.slug}), \
            data={'order_number_vendor':new_order.order_number_vendor, 'status':1, 'driver':'', 'driver_fee':10})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/sales.html')
        
