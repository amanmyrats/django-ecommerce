from random import randint
from xxlimited import new
from django.contrib import admin
from django.db import models
from django.utils.text import slugify

import admin_thumbnails

from .models import CurrencyRates, Product, Variation, ReviewRating, ProductGallery, Color, Size, Currency, \
    OtherExpense, Transport, Tax, MoneyTransfer, Income
from .utils import get_vendor


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 0


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug':('product_name','image')}
    inlines = [ProductGalleryInline, VariationInline]

    def save_model(self, request, obj, form, change):
        vendor = get_vendor(request=request)
        if vendor:
            obj.owner = vendor
            obj.slug = slugify(str(obj.product_name) + '-' + str(randint(1,1000000)) + '-' + str(vendor.id))
            super().save_model(request, obj, form, change)
            obj.slug = slugify(str(obj.product_name) + '-' + str(obj.pk))
            super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        vendor = get_vendor(request=request)
        if vendor:
            instances = formset.save(commit=False) # gets instance from memory and add to it before saving it
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.owner = vendor
                instance.save()


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active', 'detail')
    list_filter = ('product',)

    def save_model(self, request, obj, form, change):
        vendor = get_vendor(request=request)
        if vendor:
            obj.owner = vendor
            super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Currency)
admin.site.register(CurrencyRates)
admin.site.register(OtherExpense)
admin.site.register(Transport)
admin.site.register(Tax)
admin.site.register(MoneyTransfer)
admin.site.register(Income)



