import os 

from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count, UniqueConstraint
from django_unique_slugify import unique_slugify

from django_resized import ResizedImageField
from mptt.models import TreeForeignKey

from accounts.models import Account, Vendor
from category.models import Category


class Product(models.Model):
    def medium_image_name(instance, filename):
        filename = '{}_medium.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)
    def small_image_name(instance, filename):
        filename = '{}_small.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)
    def thumb_image_name(instance, filename):
        filename = '{}_thumb.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)
    brand           = models.CharField(max_length=30, blank=True, null=True)
    product_code    = models.CharField(max_length=30, null=True, blank=True)
    product_name    = models.CharField(max_length=200)
    description     = models.TextField(max_length=500, blank=True)
    slug            = models.SlugField(max_length=200, unique=True, blank=True)
    image           = ResizedImageField(size=[500,500], upload_to=medium_image_name, default='photos/products/default.jpg', blank=True, null=True)
    image_small     = ResizedImageField(size=[75,75], upload_to=small_image_name, blank=True, null=True)
    image_thumbnail = ResizedImageField(size=[45,45], upload_to=thumb_image_name, blank=True, null=True)
    owner           = models.ForeignKey(Vendor, on_delete=models.SET_NULL, blank=True, null=True)
    
    # stock           = models.IntegerField()
    category        = TreeForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_available    = models.BooleanField(default=True, blank=True)
    is_physical = models.BooleanField(default=True, null=True, blank=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)

    lowest_price    = models.FloatField(default=0, blank=True)
    highest_price   = models.FloatField(default=0, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date   = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        constraints = [UniqueConstraint(fields=['owner', 'brand', 'product_name'], name='owner_product'),]
        ordering = ['-created_date']

    def save(self, *args, **kwargs):
        unique_slugify(self, str(self.brand) + '-' + str(self.product_name))

        # Minimum and Maximum Price
        variations = Variation.objects.filter(product=self)
        prices = []
        for v in variations:
            prices.append(v.sale_price)
        try:
            self.lowest_price = min(prices)
            self.highest_price = max(prices)
        except:
            pass
        super(Product, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('vendor_product_detail', args=[self.owner.slug, self.slug])

    def __str__(self):
        if self.brand:
            return '{} - {}'.format(str(self.brand), str(self.product_name))
        else:
            return str(self.product_name)
    
    def image_url(self):
        try:
            return self.image.url
        except:
            return ''
    
    def image_small_url(self):
        try:
            return self.image_small.url
        except:
            return ''

    def image_thumbnail_url(self):
        try:
            return self.image_thumbnail.url
        except:
            return ''

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


class Color(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Variation(models.Model):
    def medium_image_name(instance, filename):
        filename = '{}_medium.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)
    def small_image_name(instance, filename):
        filename = '{}_small.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)
    def thumb_image_name(instance, filename):
        filename = '{}_thumb.jpg'.format(instance.id)
        return os.path.join('photos/products', filename)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productvariations')
    sku = models.CharField(max_length=20, null=True, blank=True)
    barcode = models.CharField(max_length=40, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, default=1)
    size = models.ForeignKey(Size, on_delete=models.PROTECT, default=1)
    quantity = models.IntegerField()
    
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True)

    initial_price = models.FloatField(default=0)
    expense_percentage = models.FloatField(default=0)
    expense_fixed = models.FloatField(default=0)

    final_price = models.FloatField(default=0, blank=True, null=True)
    sale_price = models.FloatField(default=0, blank=True, null=True)

    image           = ResizedImageField(size=[500,500], upload_to=medium_image_name, blank=True, null=True)
    # image_small     = ResizedImageField(size=[75,75], upload_to=small_image_name, blank=True, null=True)
    # image_thumbnail = ResizedImageField(size=[45,45], upload_to=thumb_image_name, blank=True, null=True)

    in_stock = models.BooleanField(default=True)
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
    
    def save(self, *args, **kwargs):
        self.final_price = self.initial_price
        if self.expense_percentage:
            self.final_price += self.final_price * self.expense_percentage/100
        if self.expense_fixed:
            self.final_price += self.expense_fixed
        
        # Stock
        if self.quantity <= 0:
            self.in_stock = False
        else:
            self.in_stock = True
        
        # if self.currency.code != 'TMT':
        #     self.final_price = self.final_tmt_price * 21
        # else:
        #     self.final_price = self.final_tmt_price
        self.sale_price = self.final_price
        super(Variation, self).save(*args, **kwargs)
        self.product.save()
        # if self.sale_price < self.product.lowest_price:
        #     self.product.lowest_price = self.sale_price
        #     self.product.save()
        # elif self.sale_price > self.product.highest_price:
        #     print('sale price is bigger than product max')
        #     self.product.highest_price = self.sale_price
        #     self.product.save()
        # super(Variation, self).save(*args, **kwargs)


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


class Currency(models.Model):
    code = models.CharField(max_length=3)
    num = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=50)

    def __str__(self):
        return str(self.code)


class CurrencyRates(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    usdequivalent = models.FloatField(default=0)
    # tmtequivalent = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.vendor, self.currency, str(self.usdequivalent))


class OtherExpense(models.Model):
    TYPES = [
        ('percentage', '%'),
        ('fixed', 'Fixed'),
    ]
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    increase_type = models.CharField(max_length=20, choices=TYPES, default='percentage')
    increase_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.variation, self.increase_type, self.increase_amount)
    

class Transport(models.Model):
    TYPES = [
        ('percentage', '%'),
        ('fixed', 'Fixed'),
    ]
    name = models.CharField(max_length=30)
    increase_type = models.CharField(max_length=20, choices=TYPES, default='percentage')
    increase_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.increase_type, self.increase_amount)


class Tax(models.Model):
    TYPES = [
        ('percentage', '%'),
        ('fixed', 'Fixed'),
    ]
    name = models.CharField(max_length=30)
    increase_type = models.CharField(max_length=20, choices=TYPES, default='percentage')
    increase_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.increase_type, self.increase_amount)


class MoneyTransfer(models.Model):
    TYPES = [
        ('percentage', '%'),
        ('fixed', 'Fixed'),
    ]
    name = models.CharField(max_length=30)
    increase_type = models.CharField(max_length=20, choices=TYPES, default='percentage')
    increase_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.increase_type, self.increase_amount)


class Income(models.Model):
    TYPES = [
        ('percentage', '%'),
        ('fixed', 'Fixed'),
    ]
    name = models.CharField(max_length=30)
    increase_type = models.CharField(max_length=20, choices=TYPES, default='percentage')
    increase_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.increase_type, self.increase_amount)