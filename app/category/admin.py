from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Category


# class CategoryAdmin(admin.ModelAdmin):
#     # prepopulated_fields = {'slug':('name',)}
#     list_display = ('name',)

admin.site.register(Category, DraggableMPTTAdmin)
