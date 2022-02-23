from .models import CartItem
from orders.models import Delivery, OrderProduct


def cart_items_vendor_list(cart_items=None):
    if cart_items is None:
        return []
    vendors = []
    for item in cart_items:
        vendors.append(item.product.owner)
    return list(set(vendors))

def cart_vendor_info(cart_items=None, user=None, cart=None):
    if cart_items is None:
        return {}
    if user is None and cart is None:
        return {}

    vendors_dict = {}
    for item in cart_items:
        vendors_dict[item.product.owner] = {}
        vendors_dict[item.product.owner]['cartitems'] = []
        vendors_dict[item.product.owner]['delivery'] = float(0)
        vendors_dict[item.product.owner]['subtotal'] = float(0)

    for item in cart_items:
        vendors_dict[item.product.owner]['cartitems'].append(item)

    for item in cart_items:
        vendors_dict[item.product.owner]['subtotal'] += item.variation.sale_price * item.quantity 

    # Calculate delivery fee for each vendor
    for v in vendors_dict:
        if len(cart_items)>0:
            vendor_delivery = Delivery.objects.filter(vendor=v).first()
            
            if vendors_dict[v]['subtotal'] < vendor_delivery.free_delivery_limit:
                vendors_dict[v]['delivery'] = vendor_delivery.fee
                vendors_dict[v]['subtotal'] += vendors_dict[v]['delivery']
            else:
                vendors_dict[v]['delivery'] = float(0)
        else:
            vendors_dict[v]['delivery'] = float(0)

    return vendors_dict

def order_vendor_info(order=None, vendor=None):
    if order is None:
        return {}

    vendors_dict = {}
    if vendor:
        order_items = OrderProduct.objects.filter(order=order, product__owner=vendor)
    else:
        order_items = OrderProduct.objects.filter(order=order)
        
    for item in order_items:
        vendors_dict[item.product.owner] = {}
        vendors_dict[item.product.owner]['orderitems'] = []
        vendors_dict[item.product.owner]['delivery'] = float(0)
        vendors_dict[item.product.owner]['subtotal'] = float(0)

    for item in order_items:
        vendors_dict[item.product.owner]['orderitems'].append(item)

    for item in order_items:
        vendors_dict[item.product.owner]['subtotal'] += item.variation.sale_price * item.quantity 

    # Calculate delivery fee for each vendor
    for v in vendors_dict:
        if len(order_items)>0:
            vendor_delivery = Delivery.objects.filter(vendor=v).first()
            
            if vendors_dict[v]['subtotal'] < vendor_delivery.free_delivery_limit:
                vendors_dict[v]['delivery'] = vendor_delivery.fee
                vendors_dict[v]['subtotal'] += vendors_dict[v]['delivery']
            else:
                vendors_dict[v]['delivery'] = float(0)
        else:
            vendors_dict[v]['delivery'] = float(0)

    return vendors_dict


def stock_available(variation=None, quantity=0):
    if variation is None or quantity==0:
        return 0
    
    try:
        if quantity<variation.quantity:
            return quantity 
        else:
            return variation.quantity
    except:
        return 0