# Generated by Django 3.1 on 2022-04-17 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_auto_20220417_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_total',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.FloatField(default=0),
        ),
    ]
