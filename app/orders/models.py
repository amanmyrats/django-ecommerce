from django.conf import settings
from django.db import models
from django.forms import FloatField
from django.utils.translation import gettext as _
from django_unique_slugify import unique_slugify

from accounts.models import Account, Vendor, Driver
from store.models import Product, Variation


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id 


class Order(models.Model):
    STATUS = (
        ('1', _('New')),
        ('2', _('On Delivery')),
        ('3', _('Delivered and Paid')),
        ('4', _('Cancelled')),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendororders')
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    order_number_vendor = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    # Address
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True)
    phone_extra = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)

    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    channel = models.CharField(max_length=40, blank=True, null=True)
    ip = models.CharField(blank=True, max_length=50)
    is_ordered = models.BooleanField(default=False)
    
    subtotal = models.FloatField(blank=True, null=True, default=0)
    delivery_fee = models.FloatField(blank=True, null=True, default=0)
    grand_total = models.FloatField(blank=True, null=True, default=0)
    
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, blank=True, null=True)
    driver_fee = models.FloatField(default=20)
    status = models.CharField(max_length=1, choices=STATUS, default='1')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        if bool(self.address_line_2):
            return f'{self.address_line_1} {self.address_line_2}'
        else:
            return f'{self.address_line_1}'
    
    def __str__(self):
        return self.order_number
    
    def save(self, *args, **kwargs):
        # self.order_number_vendor = '{}{}'.format(str(self.order_number),str(self.vendor.id))
        unique_slugify(self, str(self.order_number_vendor))
        super(Order, self).save(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderproducts')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    product_price = models.FloatField(default=0)
    package_price = models.FloatField(default=0)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
    
    def total(self):
        if self.quantity and self.product_price:
            try:
                if settings.WHOLESALE:
                    total = self.quantity * self.package_price
                    return float(total)
                else:
                    total = self.quantity * self.product_price
                    return float(total)
            except:
                return 0
        else:
            return 0


class OrderDelivery(models.Model):
    STATUS = (
        ('1', _('New')),
        ('2', _('On Delivery')),
        ('3', _('Delivered and Paid')),
        ('4', _('Cancelled')),
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendorsales')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='ordersales')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, blank=True, null=True)
    delivery_fee = models.FloatField(default=20)
    status = models.CharField(max_length=1, choices=STATUS, default='1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def vendor_total(self):
        order_items = OrderProduct.objects.filter(order=self.order, product__owner=self.vendor)
        total = 0
        for order_item in order_items:
            total += order_item.total()
        return total
    

class City(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    fee = models.FloatField(default=20)
    free_delivery_limit = models.FloatField(default=200)

    def __str__(self):
        return '{} - {}'.format(self.vendor, self.city)

