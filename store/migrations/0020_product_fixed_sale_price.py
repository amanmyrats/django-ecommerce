# Generated by Django 3.1 on 2022-02-21 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_auto_20220214_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='fixed_sale_price',
            field=models.BooleanField(default=True),
        ),
    ]
