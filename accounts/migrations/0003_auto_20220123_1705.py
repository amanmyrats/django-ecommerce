# Generated by Django 3.1 on 2022-01-23 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20220123_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingaddress',
            name='account',
        ),
        migrations.RemoveField(
            model_name='billingaddress',
            name='email',
        ),
        migrations.RemoveField(
            model_name='billingaddress',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='billingaddress',
            name='last_name',
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.account'),
            preserve_default=False,
        ),
    ]