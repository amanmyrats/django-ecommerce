# Generated by Django 3.1 on 2022-04-17 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_auto_20220319_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='driver_fee',
            field=models.FloatField(default=20),
        ),
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_fee',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number_vendor',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
