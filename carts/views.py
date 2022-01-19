from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

from store.models import Product, Variation
from .models import Cart, CartItem


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    if request.method == 'POST':
        variation_id = request.POST.get('variation_id')
        product_id = request.POST.get('product_id')

        # print('product_id', product_id)
        # print('variation_id', variation_id)
        current_user = request.user
        product_variation = None
        is_cart_item_exists = False
        
        product = get_object_or_404(Product, id=product_id)
        product_variation = get_object_or_404(Variation, id=variation_id)
        # print('product', product)
        # print('product_variation', product_variation)
        if current_user.is_authenticated:
            is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variation=product_variation).exists()
            # print('is_cart_item_exists', is_cart_item_exists)
            if is_cart_item_exists:
                cart_item = CartItem.objects.get(product=product, user=current_user, variation=product_variation)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product = product, user = current_user, variation=product_variation, quantity = 1)
                cart_item.save()

            return redirect('cart')
        else: # If the user is not authenticated
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id = _cart_id(request)
                )
                cart.save()
            
            is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart, variation=product_variation).exists()

            if is_cart_item_exists:
                cart_item = CartItem.objects.get(product=product, cart=cart, variation=product_variation) 
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product = product, variation=product_variation, cart = cart, quantity = 1)
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
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        print('cart_items', cart_items)
        for cart_item in cart_items:
            total += (cart_item.variation.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total +tax

    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.variation.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total
    } 
    return render(request, 'store/checkout.html', context)