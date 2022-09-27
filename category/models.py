from multiprocessing.connection import answer_challenge
from django.db import models
from django.urls import reverse
# from django_resized import ResizedImageField
from django.db.models import Avg, Count, UniqueConstraint

from mptt.models import MPTTModel, TreeForeignKey
from django_unique_slugify import unique_slugify


class Category(MPTTModel):
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(max_length=250, blank=True)
    image = models.ImageField(upload_to='photos/categories', default='photos/categories/default.jpg', blank=True, null=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        constraints = [UniqueConstraint(fields=['parent', 'slug'], name='parentslug'),]
    
    class MPTTMeta:
        order_insertion_by = ['name']

    def get_url(self):
        return reverse('products_by_category', args=[self.get_slug_list()[-1],])
    
    def __str__(self):
        return self.name
    
    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i+1]))
        return slugs
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        return super().save(*args, **kwargs)