# Generated by Django 3.1 on 2022-04-24 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20220418_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.city'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='fee',
            field=models.FloatField(default=20),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='free_delivery_limit',
            field=models.FloatField(default=200),
        ),
    ]
