# Generated by Django 3.1 on 2022-03-18 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_auto_20220214_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='channel',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
