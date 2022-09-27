# Generated by Django 3.1 on 2022-05-16 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0043_variation_min_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='items_in_package',
            field=models.IntegerField(blank=True, default=1),
        ),
        migrations.AlterField(
            model_name='variation',
            name='package_price',
            field=models.FloatField(blank=True, default=0),
        ),
    ]