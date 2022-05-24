# Generated by Django 3.1 on 2022-01-23 15:52

from django.db import migrations
import django_resized.forms
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20220123_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=75, size=[200, 200], upload_to=store.models.Product.medium_image_name),
        ),
    ]