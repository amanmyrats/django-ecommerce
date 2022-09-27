import pytest 

from django.test import TestCase
from pytest import fixture

from orders.models import Payment, Order, OrderDelivery, OrderProduct, City, Delivery
from accounts.models import Account, Vendor
from accounts.accounts_tests.test_models import user, vendor
from store.tests_store.test_models import product, variation, color_yellow, size_small


@pytest.fixture
def payment(db, user):
    return Payment.objects.create(
        user=user,
        payment_id='someid12345',
        payment_method='cash',
        amount_paid=1000,
        status='paid'
    )

@pytest.fixture
def order(db, user, vendor, payment):
    return Order.objects.create(
        user=user, vendor=vendor, payment=payment, order_number='No1', order_number_vendor='No1vendor',
        first_name='Aman', last_name='Myrat', address_line_1='Some address here',
        city='Asgabat', order_note='Some note from client', ip='111.111.111.111',
    )

@pytest.fixture
def city(db):
    return City.objects.create(name='Asgabat')

def test_payment_model(db, user):
    payment = Payment.objects.create(
        user=user,
        payment_id='someid12345',
        payment_method='cash',
        amount_paid=1000,
        status='paid'
    )
    assert isinstance(payment, Payment)
    assert payment.__str__()=='someid12345'

def test_order_model(db, user, vendor, payment):
    order = Order.objects.create(
        user=user, vendor=vendor, payment=payment, order_number='No1', order_number_vendor='No1vendor',
        first_name='Aman', last_name='Myrat', address_line_1='Some address here',
        city='Asgabat', order_note='Some note from client', ip='111.111.111.111',
    )
    assert order.full_name()=='Aman Myrat'
    assert order.full_address()=='Some address here'
    assert order.__str__()=='No1'

def test_orderproduct_model(db, user, order, payment, product, variation):
    orderproduct = OrderProduct.objects.create(
        order=order, payment=payment, user=user, product=product, variation=variation,
        quantity=1, product_price=10
    )
    assert isinstance(orderproduct, OrderProduct)
    assert orderproduct.__str__()=='jeans'
    assert orderproduct.total()==10

def test_city_model(db):
    city = City.objects.create(name='Asgabat')
    assert city.__str__()=='Asgabat'

def test_delivery_model(db, vendor, city):
    delivery = Delivery.objects.create(vendor=vendor, city=city)
    assert delivery.__str__()=='sargajak - Asgabat'

def test_orderdelivery_model(db, vendor, order):
    orderdelivery = OrderDelivery.objects.create(vendor=vendor, order=order)
    assert isinstance(orderdelivery, OrderDelivery)
    assert orderdelivery.vendor_total()==0