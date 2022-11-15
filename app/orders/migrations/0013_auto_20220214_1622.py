# Generated by Django 3.1 on 2022-02-14 11:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_auto_20220214_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdelivery',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdelivery',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
