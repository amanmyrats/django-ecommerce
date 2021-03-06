# Generated by Django 3.1 on 2022-01-29 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_auto_20220129_0840'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='product',
            name='owner_product',
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('owner', 'brand', 'product_name'), name='owner_product'),
        ),
    ]
