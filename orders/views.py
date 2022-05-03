import datetime
import imp
import json
from django.core.checks import messages

from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from accounts.models import BillingAddress
from .models import Order, OrderProduct, Payment, OrderDelivery
from carts.models import Cart, CartItem
from store.models import Product, Variation
from .forms import OrderForm

from carts.utils import order_vendor_info, stock_available, cart_items_vendor_list, cart_vendor_info


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.variation.sale_price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()



        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    
    return JsonResponse(data)

@login_required
def place_order(request, total=0, quantity=0):
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

    # If the cart count is less than or equal to 0, then redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    vendor_info_of_cart = cart_vendor_info(cart_items=cart_items, user=current_user)

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        # Check the item's stock situation
        initial_quantity = cart_item.quantity
        cart_item.quantity = stock_available(variation=cart_item.variation, quantity=cart_item.quantity)
        if initial_quantity == cart_item.quantity:
            total += (cart_item.variation.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
        elif cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
            total += (cart_item.variation.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
        
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            # Loop through vendors
            cart_items = CartItem.objects.filter(user=request.user)
            vendors = cart_items_vendor_list(cart_items=cart_items)
            # Store all the billing information inside Order table
            order_number = None
            for vendor in vendors:
                data = Order()
                data.user = current_user

                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.phone_extra = form.cleaned_data['phone_extra']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                data.vendor = vendor

                data.delivery_fee = vendor_info_of_cart.get(vendor).get('delivery')
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                if order_number == None:
                    # Generate order number
                    yr = int(datetime.date.today().strftime('%Y'))
                    mt = int(datetime.date.today().strftime('%m'))
                    dt = int(datetime.date.today().strftime('%d'))
                    d = datetime.date(yr, mt, dt)
                    current_date = d.strftime("%Y%m%d") #20120305
                    order_number = current_date + str(data.id)
                data.order_number = order_number
                data.order_number_vendor = '{}{}'.format(str(order_number), str(vendor.id))
                data.save()

                # Save lastest billing address
                billingaddress.phone_extra = data.phone_extra
                billingaddress.address_line_1 = data.address_line_1
                billingaddress.address_line_2 = data.address_line_2
                billingaddress.country = data.country
                billingaddress.state = data.state
                billingaddress.city = data.city
                billingaddress.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                order.is_ordered = True
                order.save()

                # Move the cart items to Order Product table
                subtotal = 0
                for item in cart_items:
                    # Check the item's stock situation
                    if item.product.owner == vendor:
                        initial_quantity = item.quantity
                        item.quantity = stock_available(variation=item.variation, quantity=item.quantity)
                        if initial_quantity == item.quantity:
                            pass
                        elif item.quantity <= 0:
                            item.delete()
                            continue
                        else:
                            item.save()
                        
                        orderproduct = OrderProduct()
                        orderproduct.order_id = order.id
                        orderproduct.user_id = request.user.id
                        orderproduct.product_id = item.product_id
                        orderproduct.variation_id = item.variation_id
                        orderproduct.product_price = item.variation.sale_price
                        orderproduct.quantity = item.quantity
                        orderproduct.ordered = True
                        orderproduct.save()

                        subtotal += orderproduct.quantity*orderproduct.product_price

                    # Reduce the quantity of the sold products
                    product = Variation.objects.get(id=item.variation.id)
                    product.quantity -= item.quantity
                    product.save()
                
                # Calculate subtotal and grandtotal of Order
                order.subtotal = subtotal
                order.grand_total = subtotal + order.delivery_fee
                order.save()



            total_delivery = 0
            new_order = Order.objects.filter(order_number=order_number)
            for vendor_order in new_order:
                total_delivery += vendor_order.delivery_fee

            # # Create orderdelivery info for vendor
            vendors_dict = order_vendor_info(order=order)
            # # print('vendors_dict', type(vendors_dict))
            # for vendor, values in vendors_dict.items():
            #     sale = OrderDelivery()
            #     sale.vendor = vendor
            #     sale.order = order
            #     sale.delivery_fee = values.get('delivery')
            #     sale.save()

            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order recieved email to customer
            # mail_subject = 'Thank you for your order!'
            # message = render_to_string('orders/order_recieved_email.html', {
            #     'user': request.user,
            #     'order': order,
            # })
            # to_email = request.user.email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.send()

            # # Send order number and transaction id back to sendData method via JsonResponse
            # data = {
            #     'order_number': order.order_number,
            #     # 'transID': payment.payment_id,
            # }
           
           
            context = {
                'vendors_dict':vendors_dict,
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'total_delivery': total_delivery,
                'grand_total': grand_total,
            }
            # print(str(redirect('order_complete', order_no=order.order_number)))
            return redirect('order_complete', order_no=order_number)
            # return render(request, 'orders/order_complete.html', context)
    else:
        return redirect('checkout')


@login_required
def order_complete(request, order_no=None):
    order_number = order_no
    print('order_number', order_number)
    # transID = request.GET.get('transID')
    if order_number is None:
        # messages
        return redirect('home')
    
    current_user = request.user
        
    try:
        orders = Order.objects.filter(order_number=order_number, is_ordered=True)
        subtotal = 0
        total_delivery = 0
        for order in orders:
            # ordered_products = OrderProduct.objects.filter(order_id=order.id)

            # for i in ordered_products:
            subtotal += order.subtotal
            

            # new_order = OrderDelivery.objects.filter(order=order)
            # for delivery in new_order:
            total_delivery += order.delivery_fee

            # vendors_dict = order_vendor_info(order=order)
        
        grand_total = subtotal + total_delivery
        # payment = Payment.objects.get(payment_id=transID)

        context = {
            # 'vendors_dict':vendors_dict,
            'orders': orders,
            # 'ordered_products': ordered_products,
            # 'order_number': order.order_number,
            # 'transID': payment.payment_id,
            # 'payment': payment,
            'total_delivery':total_delivery,
            'subtotal': subtotal,
            'grand_total':grand_total,
        }
        return render(request, 'orders/order_complete_test.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
