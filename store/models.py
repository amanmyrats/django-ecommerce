from enum import unique
from pyexpat.errors import messages
from unicodedata import name
from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError

from accounts.models import Account
from category.models import Category


class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    image           = models.ImageField(upload_to='photos/products')
    # stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category   = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
    def has_no_variation(self):
        has_no_variation_exists = Variation.objects.filter(product=self, color__name='No Variation', size__name='No Variation').exists()
        print('has_no_variation_exists', has_no_variation_exists)
        if has_no_variation_exists:
            return True
        else:
            return False
    
    def has_no_variation_id(self):
        if self.has_no_variation():
            has_no_variation = Variation.objects.filter(product=self, color__name='No Variation', size__name='No Variation')
            return has_no_variation[0].id
        else:
            return "" 

    def colors(self):
        variations = Variation.objects.filter(product = self)
        colorlist = []
        for var in variations:
            colorlist.append(var.color)
        return list(set(colorlist))
    
    def sizes(self):
        variations = Variation.objects.filter(product=self)
        sizelist = []
        for var in variations:
            sizelist.append(var.size)
        return list(set(sizelist))

    def nocolor(self):
        variations = Variation.objects.filter(product = self)
        colorlist = []
        for var in variations:
            colorlist.append(var.color)
        colorlist = list(set(colorlist))
        if colorlist[0].name == 'No Variation':
            return True
        return False

    def nosize(self):
        variations = Variation.objects.filter(product = self)
        sizelist = []
        for var in variations:
            sizelist.append(var.size)
        sizelist = list(set(sizelist))
        print('sizelist', sizelist)
        if sizelist[0].name == 'No Variation':
            return True
        return False

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def count_reviews(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def lowest_price(self):
        variations = Variation.objects.filter(product=self)
        prices = []
        for v in variations:
            prices.append(v.price)
        try:
            return min(prices)
        except:
            return 0
    
    def highest_price(self):
        variations = Variation.objects.filter(product=self)
        prices = []
        for v in variations:
            prices.append(v.price)
        try:
            return max(prices)
        except:
            return 0
    

class Color(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, default=1)
    size = models.ForeignKey(Size, on_delete=models.PROTECT, default=1)
    quantity = models.IntegerField()
    price = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_data = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['product', 'color', 'size'], name='single_variation')]

    @property
    def detail(self):
        return 'list(self.variations.all())'

    def __unicode__(self):
        return self.product
    
    def __str__(self):
        return str(self.color) + str(self.size)


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'Product Galleries'