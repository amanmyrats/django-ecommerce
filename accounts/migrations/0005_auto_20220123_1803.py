# Generated by Django 3.1 on 2022-01-23 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20220123_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='address_line_2',
            field=models.CharField(blank=True, default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='country',
            field=models.CharField(blank=True, default='Turkmenistan', max_length=50),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='state',
            field=models.CharField(blank=True, default=1, max_length=50),
            preserve_default=False,
        ),
    ]
