# Generated by Django 3.1 on 2022-01-28 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_auto_20220128_1704'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='variation',
            name='single_variation',
        ),
        migrations.AddConstraint(
            model_name='variation',
            constraint=models.UniqueConstraint(fields=('owner', 'product', 'color', 'size'), name='single_variation'),
        ),
    ]