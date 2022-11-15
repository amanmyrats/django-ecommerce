# Generated by Django 3.1 on 2022-02-21 09:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_auto_20220221_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='final_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='variation',
            name='final_tmt_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='variation',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='UnitPriceCalculator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('increase_type', models.CharField(choices=[('percentage', '%'), ('fixed', 'Fixed')], default='percentage', max_length=20)),
                ('increase_amount', models.FloatField(default=0)),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.variation')),
            ],
        ),
    ]
