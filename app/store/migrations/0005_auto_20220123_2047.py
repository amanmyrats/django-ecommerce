# Generated by Django 3.1 on 2022-01-23 15:47

from django.db import migrations
import django_resized.forms
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20220118_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_thumbnail',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='JPEG', keep_meta=True, null=True, quality=75, size=[], upload_to=store.models.Product.thumb_image_name),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=75, size=[], upload_to=store.models.Product.medium_image_name),
        ),
    ]
