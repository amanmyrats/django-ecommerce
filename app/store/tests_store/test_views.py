import json

import pytest

from django.urls import reverse
from accounts.models import Account, Vendor
from category.models import Category

from orders.test_orders.test_views import products
from accounts.accounts_tests.test_models import vendor, user
from store.models import Product, Variation
from store.forms import ProductModelForm, VariationModelForm


# @pytest.mark.parametrize( ['product_name', 'description'],
#             [('product1','description1' ),
#             ('','some description2' )])

def test_productlistview_view(db, client, products):
    random_vendor = Vendor.objects.all().first()
    random_product = Product.objects.all().first()
    random_category = Category.objects.all().first()
    print('random category', random_category)
    response = client.get(reverse('store'))
    assert response.status_code==200
    response = client.get(reverse('store_vendor', kwargs={'vendor_slug':random_vendor.slug}))
    assert response.status_code==200
    response = client.get(reverse('products_by_category', kwargs={'hierarchy':random_category.get_slug_list()[-1]}))
    assert response.status_code==200

def test_productlistview_view_with_filter_parameters(db, client, products):
    random_vendor = Vendor.objects.all().first()
    random_product = Product.objects.all().first()
    random_category = Category.objects.all().first()
    # Vendor based store
    data = {'min_price':1, 'max_price':2000, 'order':'hightolow', 'category':random_category.id}
    response = client.get(reverse('store_vendor', kwargs={'vendor_slug':random_vendor.slug}), data=data)
    assert response.status_code==200
    assert b'Add to Cart' in response.content # There is at least material
    # Vendor based store with different ordering
    data = {'min_price':1, 'max_price':2000, 'order':'lowtohigh', 'category':random_category.id}
    response = client.get(reverse('store_vendor', kwargs={'vendor_slug':random_vendor.slug}), data=data)
    assert response.status_code==200
    assert b'Add to Cart' in response.content # There is at least material
    # Category based store
    data = {'min_price':1, 'max_price':2000, 'order':'hightolow', 'vendor':random_vendor.id}
    response = client.get(reverse('products_by_category', kwargs={'hierarchy':random_category.get_slug_list()[-1]}), data=data)
    assert response.status_code==200
    assert b'Add to Cart' in response.content # There is at least material


def test_productdetailview_view(db, client, products):
    random_vendor = Vendor.objects.all().first()
    random_product = Product.objects.all().first()
    response = client.get(reverse('vendor_product_detail', kwargs={'vendor_slug':random_vendor.slug, 'product_slug':random_product.slug}))
    assert response.status_code==200

def test_productdetailview_view_with_logged_in_user(db, client, products):
    # User is not logged in
    response = client.get(reverse('list_product'))
    assert response.status_code==302

    # User is not vendor
    client.login(phone_number=65555555, password='aman')
    response = client.get(reverse('list_product'))
    assert response.status_code==302

    # User is vendor and logged in
    random_vendor = Vendor.objects.all().first()
    random_product = Product.objects.all().first()
    client.login(phone_number=61111111, password='aman')
    response = client.get(reverse('vendor_product_detail', kwargs={'vendor_slug':random_vendor.slug, 'product_slug':random_product.slug}))
    assert response.status_code==200

def test_list_product(db, client, products):
    client.login(phone_number=61111111, password='aman')
    response = client.get(reverse('list_product'))
    assert response.status_code==200

def test_add_product_view(db, client, products):
    # User not logged in
    response = client.get(reverse('add_product'))
    assert response.status_code==302
    # User is logged in
    test_user = Account.objects.get(phone_number=61111111)
    test_category = Category.objects.all().first()
    client.login(phone_number=test_user.phone_number, password='aman')
    response = client.get(reverse('add_product'))
    assert response.status_code==200
    # Add new product, POST request
    new_product_data = {'owner':test_user.id, 'product_name':'new product', 'description':'some description', 'category':test_category.id}
    response = client.post(reverse('add_product'), data=new_product_data)
    assert response.status_code==302

def test_edit_product_view(db, client, products):
    # With anonymous user
    response = client.get(reverse('edit_product', kwargs={'product_slug':None}))
    assert response.status_code==302
    # Logged in user with non-valid product_slug
    client.login(phone_number=65555555, password='aman')
    response = client.get(reverse('edit_product', kwargs={'product_slug':None}))
    assert response.status_code==302
    # Logged in non vendor user
    random_product = Product.objects.all().first()
    client.login(phone_number=65555555, password='aman')
    response = client.get(reverse('edit_product', kwargs={'product_slug':random_product.slug}))
    assert response.status_code==302
    # Logged in vendor, GET request
    client.login(phone_number=61111111, password='aman')
    response = client.get(reverse('edit_product', kwargs={'product_slug':random_product.slug}))
    assert response.status_code==200
    # Send POST with Product form
    data = {'product_name':random_product.product_name, 'description':random_product.description, 
            'color':'Yellow', 'size':'S', 'quantity':10, 
            'productvariations-TOTAL_FORMS':'0', 'productvariations-INITIAL_FORMS':'0', 
            'productvariations-MIN_NUM_FORMS':0, 'productvariations-MAX_NUM_FORMS':1000}
    response = client.post(reverse('edit_product', kwargs={'product_slug':random_product.slug}), data=data)
    assert response.status_code==302
    response = client.get(response.url)
    assert b'success' in response.content
    # Send invalid form
    # data = {
    #         'product_name':'test' , 'description':'', 
    #         'color':'Yellow', 'size':'S', 'quantity':10, 
    #         'productvariations-TOTAL_FORMS':'0', 'productvariations-INITIAL_FORMS':'0', 
    #         'productvariations-MIN_NUM_FORMS':0, 'productvariations-MAX_NUM_FORMS':1000}
    # response = client.post(reverse('edit_product', kwargs={'product_slug':random_product.slug}), data=data)
    # assert response.status_code==200

def test_variation_price_view(db, products, client):
    random_product = Product.objects.all().last()
    test_variation = Variation.objects.filter(product=random_product).first()
    test_color = Variation.objects.filter(product=random_product).first().color
    test_size = Variation.objects.filter(product=random_product).first().size
    expected_price = Variation.objects.filter(product=random_product).first().sale_price
    response = client.get(reverse('variation_price'), data={'product_id':random_product.id, 'color_id':test_color.id, 'size_id':test_size.id})
    response = json.loads(response.content)
    assert response['price']==expected_price
    
def test_submit_review_view(db, client, products):
    random_product = Product.objects.all().first()
    data = {'subject':'review title', 'review':'very good product', 'rating':10}
    # User not logged in
    response = client.post(reverse('submit_review', kwargs={'product_id':random_product.id}), data=data)
    assert response.status_code==302
    # User logged in
    client.login(phone_number=61111111, password='aman')
    response = client.post(reverse('submit_review', kwargs={'product_id':random_product.id}), data=data)
    assert response.status_code==302
    