from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext as _
from django.conf import settings

from store.models import Product, Variation
from .models import Cart, CartItem
from accounts.models import BillingAddress

from .utils import cart_vendor_info, stock_available

def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    if request.method == 'POST':
        variation_id = request.POST.get('variation_id')
        product_id = request.POST.get('product_id')
        requested_quantity = 1

        # print('product_id', product_id)
        # print('variation_id', variation_id)
        current_user = request.user
        product_variation = None
        is_cart_item_exists = False
        
        product = get_object_or_404(Product, id=product_id)
        product_variation = get_object_or_404(Variation, id=variation_id, is_active=True)
        if not product_variation.in_stock:
            messages.info(request, _('Product variations is out of stock.'))
            return redirect('cart')
        # print('product', product)
        # print('product_variation', product_variation)
        if current_user.is_authenticated:
            is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variation=product_variation).exists()
            # print('is_cart_item_exists', is_cart_item_exists)
            if is_cart_item_exists:
                cart_item = CartItem.objects.get(product=product, user=current_user, variation=product_variation)
                # Check the item's stock situation
                cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity+requested_quantity)
                if cart_item.quantity <= 0:
                    # messages.info(request, _('Product variations is out of stock.'))
                    cart_item.delete()
                else:
                    cart_item.save()
            else:
                
                cart_item = CartItem.objects.create(product = product, user = current_user, variation=product_variation, quantity = requested_quantity)
                # Check the item's stock situation
                cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity)
                if cart_item.quantity <= 0:
                    # messages.info(request, _('Product variations is out of stock.'))
                    cart_item.delete()
                else:
                    cart_item.save()
                # cartdelivery = CartDelivery.objects.create(user=current_user, vendor=product.owner)
                # cartdelivery.save()

            return redirect('cart')
        else: # If the user is not authenticated
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id = _cart_id(request)
                )
                cart.save()
            
            is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart, variation=product_variation, user=None).exists()

            if is_cart_item_exists:
                cart_item = CartItem.objects.get(product=product, cart=cart, variation=product_variation, user=None) 
                # Check the item's stock situation
                cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity+requested_quantity)
                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()
            else:
                cart_item = CartItem.objects.create(product = product, variation=product_variation, cart = cart, quantity = 1)
                # Check the item's stock situation
                cart_item.quantity = stock_available(variation=cart_item.variation, quantity=requested_quantity)
                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect ('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        vendors_dict = {}
        total_delivery = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            vendors_dict = cart_vendor_info(cart_items=cart_items, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            vendors_dict = cart_vendor_info(cart_items=cart_items, cart=cart)

        for cart_item in cart_items:
            # Check the item's stock situation
            initial_quantity = cart_item.quantity
            cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity)
            if initial_quantity == cart_item.quantity:
                if settings.WHOLESALE:
                    total += (cart_item.variation.package_price * cart_item.quantity)
                else:
                    total += (cart_item.variation.sale_price * cart_item.quantity)
                quantity += cart_item.quantity
            elif cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
                total += (cart_item.variation.sale_price * cart_item.quantity)
                quantity += cart_item.quantity
        for v in vendors_dict:
            total_delivery += vendors_dict[v]['delivery']

        tax = (2 * total)/100
        grand_total = total + total_delivery

    except ObjectDoesNotExist:
        pass
    context = {
        'vendors_dict':vendors_dict,
        'cart_items':cart_items,
        'quantity':quantity,
        'total':total,
        'total_delivery':total_delivery,
        'grand_total':grand_total
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    current_user = request.user

    # If there is no billing address then create one
    try:
        billingaddress = BillingAddress.objects.get(user=current_user)
    except:
        # if there is more than 1 billing address that belong to user, delete all
        billingaddresses = BillingAddress.objects.filter(user=current_user)
        for billaddr in billingaddresses:
            billaddr.delete()
        billingaddress = BillingAddress()
        billingaddress.user = current_user
        billingaddress.save()

    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            vendors_dict = cart_vendor_info(cart_items=cart_items, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            vendors_dict = cart_vendor_info(cart_items=cart_items, cart=cart)
            
        for cart_item in cart_items:
            # Check the item's stock situation
            initial_quantity = cart_item.quantity
            cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity)
            if initial_quantity == cart_item.quantity:
                if settings.WHOLESALE:
                    total += (cart_item.variation.package_price * cart_item.quantity)
                else:
                    total += (cart_item.variation.sale_price * cart_item.quantity)
                quantity += cart_item.quantity
            elif cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
                total += (cart_item.variation.sale_price * cart_item.quantity)
                quantity += cart_item.quantity
        
        total_delivery = 0
        for v in vendors_dict:
            total_delivery += vendors_dict[v]['delivery']

        tax = (2 * total)/100
        grand_total = total + total_delivery
    except ObjectDoesNotExist:
        pass
    context = {
        'vendors_dict':vendors_dict,
        'cart_items':cart_items,
        'quantity':quantity,
        'total':total,
        'total_delivery':total_delivery,
        'grand_total':grand_total, 
        'billingaddress':billingaddress,
    } 
    return render(request, 'store/checkout.html', context)