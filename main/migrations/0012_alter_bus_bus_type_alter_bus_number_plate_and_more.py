# Generated by Django 4.1.3 on 2024-04-14 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_feature_features_feature_unique_feature_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='bus_type',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='bus',
            name='number_plate',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='bus',
            name='status',
            field=models.CharField(max_length=10),
        ),
    ]
