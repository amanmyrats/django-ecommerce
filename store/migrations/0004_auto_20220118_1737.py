# Generated by Django 3.1 on 2022-01-18 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20220117_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='color',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='store.color'),
        ),
        migrations.AlterField(
            model_name='variation',
            name='size',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='store.size'),
        ),
    ]