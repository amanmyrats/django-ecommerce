import pytest

from django.core.management import call_command
from django.urls import reverse
from django.contrib.auth import authenticate

from store.models import Product
from orders.models import Order
from accounts.accounts_tests.test_models import user
from accounts.models import Account


@pytest.fixture(scope='function')
def products(django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'allfixture.json')

@pytest.mark.django_db
def test_total_products(products):
    assert Product.objects.all().count()>1

def test_place_order_with_logged_out_user(db, client, products):
    response = client.get(reverse('place_order'))
    assert response.status_code==302

def test_place_order_with_logged_in_user(db, client, products, user):
    client.login(phone_number=61111111, password='aman')
    response = client.get(reverse('place_order'))
    assert response.status_code==302
    # print('get response', response)
    assert 'checkout' in response.url

    # post request with valid form
    response = client.post(reverse('place_order'), data={
        'first_name':'aman', 'last_name':'myrat', 'phone':61111111, 'phone_extra':61111111, 'email':'aman@aman.aman', 
        'address_line_1':'asgabat', 'address_line_2':'mir1', 'country':'turkmenistan', 'state':'ahal', 'city':'asgabat',
        'order_note':'dowman getirewerin!!'
    })
    # print('post response', response)
    assert response.status_code==302
    assert 'order_complete' in response.url

def test_place_order_without_billing_address(db, products, user, client):
    client.login(phone_number=user.phone_number, password='aman')
    response = client.get(reverse('place_order'))
    print('response of without billing', response)
    assert response.status_code==302

def test_order_complete(db, client, products, user):
    last_order = Order.objects.all().last()
    client.login(phone_number=61111111, password='aman')
    response = client.get(reverse('order_complete', kwargs={'order_no':last_order.order_number}))
    assert response.status_code==200