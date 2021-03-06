from django.conf import settings

from django.db import models
from accounts.models import Account, Vendor

from store.models import Product, Variation
from orders.models import Delivery


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product,  on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        if settings.WHOLESALE:
            return self.variation.package_price * self.quantity
        else:
            return self.variation.sale_price * self.quantity

    def __unicode__(self):
        return self.product
