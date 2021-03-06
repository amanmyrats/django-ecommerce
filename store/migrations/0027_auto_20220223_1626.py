# Generated by Django 3.1 on 2022-02-23 11:26

from django.db import migrations, models
import django_resized.forms
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0026_auto_20220223_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='in_stock',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=100, size=[500, 500], upload_to=store.models.Product.medium_image_name),
        ),
    ]
