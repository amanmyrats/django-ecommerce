from pydoc import cli
from django.urls import reverse
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware

from carts import views, models
from orders.models import Delivery
from store.models import Color, Size, Product, Variation
from accounts.models import Account, Vendor


class CartsViewsTest(TestCase):
    
    def setUp(self):
        self.request_anon = RequestFactory().get(reverse('store'))
        self.request_anon.user = AnonymousUser()
        middlew = SessionMiddleware()
        middlew.process_request(self.request_anon)
        self.request_anon.session.save()
        self.cart_id = self.request_anon.session

        self.new_user =  Account.objects.create(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number='61111111', is_active=True, is_staff=True
                        )
        self.new_user.set_password('aman')
        self.new_user.save()
        self.vendor = Vendor()
        self.vendor.user = self.new_user
        self.vendor.official_name = 'sargajak'
        self.vendor.save()

        self.delivery = Delivery.objects.create(vendor=self.vendor)
        self.delivery.save()

        self.cart = models.Cart.objects.create(cart_id='someid')
        self.color = Color.objects.create(name='yellow')
        self.color2 = Color.objects.create(name='blue')
        self.size = Size.objects.create(name='S')
        self.size2 = Size.objects.create(name='M')
        self.product = Product.objects.create(product_name='product1', description='somedesc', owner=self.vendor)
        self.variation = Variation.objects.create(product=self.product,
            quantity=10, initial_price=5, color=self.color, size=self.size)
        self.variation2 = Variation.objects.create(product=self.product,
            quantity=10, initial_price=5, color=self.color2, size=self.size2)
    
        self.request_logged = RequestFactory().get(reverse('store'))
        self.request_logged.user = self.new_user

    def test_cart_id(self):
        response = views._cart_id(self.request_anon)
        self.assertEqual(response, self.cart_id.session_key)
    
    def test_add_cart(self):
        c = Client()
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation.id, 'product_id':self.product.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation.id, 'product_id':self.product.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation.id, 'product_id':self.product.id})
        self.assertEqual(response.status_code, 302)
        # test remove cart
        cart_item_id = models.CartItem.objects.all().first()
        response = c.get(reverse('remove_cart', kwargs={'product_id':self.product.id, 'cart_item_id':cart_item_id.id}))
        self.assertEqual(response.status_code, 302)
        # test remove cart item
        cart_item_id = models.CartItem.objects.all().first()
        response = c.get(reverse('remove_cart_item', kwargs={'product_id':self.product.id, 'cart_item_id':cart_item_id.id}))
        self.assertEqual(response.status_code, 302)
        
        # with authenticated user
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation2.id, 'product_id':self.product.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation2.id, 'product_id':self.product.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation2.id, 'product_id':self.product.id})
        self.assertEqual(response.status_code, 302)
        cart_item_id = models.CartItem.objects.all().first()
        response = c.get(reverse('remove_cart', kwargs={'product_id':self.product.id, 'cart_item_id':cart_item_id.id}))
        self.assertEqual(response.status_code, 302)
        # test remove cart item
        cart_item_id = models.CartItem.objects.all().first()
        response = c.get(reverse('remove_cart_item', kwargs={'product_id':self.product.id, 'cart_item_id':cart_item_id.id}))
        self.assertEqual(response.status_code, 302)

        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation2.id, 'product_id':self.product.id})
        response = c.post(reverse('add_cart', kwargs={'product_id':self.product.id}), 
            data={'variation_id':self.variation2.id, 'product_id':self.product.id})
        items = models.CartItem.objects.all()
        print('item', items)
        # test cart
        response = c.get(reverse('cart'))
        self.assertTrue(response.status_code, 200)

        c.logout()
        response = c.get(reverse('cart'))
        self.assertTrue(response.status_code, 200)

        # test checkout
        c.login(phone_number=self.new_user.phone_number, password='aman')
        response = c.get(reverse('checkout'))
        self.assertTrue(response.status_code, 200)

