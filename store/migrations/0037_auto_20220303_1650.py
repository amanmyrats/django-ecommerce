# Generated by Django 3.1 on 2022-03-03 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_auto_20220303_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='highest_price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='lowest_price',
            field=models.FloatField(default=0),
        ),
    ]