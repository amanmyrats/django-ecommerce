from django.test import TestCase

from carts.models import Cart, CartItem
from store.models import Color, Product, Size, Variation
from accounts.models import Account


class CartModelsTest(TestCase):

    def setUp(self):
        pass
        self.new_user =  Account.objects.create(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number='61111111', is_active=True, is_staff=True
                        )
        self.cart = Cart.objects.create(cart_id='someid')
        self.color = Color.objects.create(name='yellow')
        self.size = Size.objects.create(name='S')
        self.product = Product.objects.create(product_name='product1', description='somedesc')
        self.variation = Variation.objects.create(product=self.product,
            quantity=2, initial_price=2, color=self.color, size=self.size)
    
    def test_cart(self):
        self.assertEqual(self.cart.cart_id, 'someid')
        self.assertEqual(self.cart.__str__(), 'someid')
        self.assertIsInstance(self.cart, Cart)
    
    def test_cartitem(self):
        cart_item = CartItem.objects.create(
            user=self.new_user,
            product=self.product,
            variation=self.variation,
            cart=self.cart,
            quantity=1,
        )
        self.assertEqual(CartItem.objects.all().count(),1)
        print('subtotal', cart_item.sub_total())
        self.assertEqual(cart_item.sub_total(), 2)
        self.assertEqual(cart_item.__unicode__(), self.product)