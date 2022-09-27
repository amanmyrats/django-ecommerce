# Generated by Django 3.1 on 2022-02-14 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_driver'),
        ('carts', '0002_auto_20220118_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartDelivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carts.cart')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.vendor')),
            ],
        ),
        migrations.AddConstraint(
            model_name='cartdelivery',
            constraint=models.UniqueConstraint(fields=('cart', 'vendor'), name='cart_vendor'),
        ),
    ]