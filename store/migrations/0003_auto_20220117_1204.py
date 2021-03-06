# Generated by Django 3.1 on 2022-01-17 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_product_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.color'),
        ),
        migrations.AlterField(
            model_name='variation',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.size'),
        ),
    ]
