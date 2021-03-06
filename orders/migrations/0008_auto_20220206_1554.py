# Generated by Django 3.1 on 2022-02-06 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_driver'),
        ('orders', '0007_auto_20220206_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='delivery_fee',
            field=models.FloatField(default=20),
        ),
        migrations.AddField(
            model_name='sale',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.driver'),
        ),
    ]
