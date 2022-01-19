from django.contrib import admin
from django.db import models

import admin_thumbnails

from .models import Product, Variation, ReviewRating, ProductGallery, Color, Size


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [ProductGalleryInline, VariationInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active', 'detail')
    list_filter = ('product',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(Color)
admin.site.register(Size)



