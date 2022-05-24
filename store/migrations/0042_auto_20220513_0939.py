# Generated by Django 3.1 on 2022-05-13 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0041_product_items_in_package'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='items_in_package',
        ),
        migrations.AddField(
            model_name='variation',
            name='items_in_package',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='variation',
            name='package_price',
            field=models.FloatField(default=0),
        ),
    ]