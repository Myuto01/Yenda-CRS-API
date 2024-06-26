# Generated by Django 4.1.3 on 2024-04-16 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_remove_feature_unique_feature_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('license_number', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('nrc_number', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('phone_number', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('passport_number', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('license_image', models.ImageField(blank=True, null=True, upload_to='media/license_image/')),
                ('nrc_image', models.ImageField(blank=True, null=True, upload_to='media/nrc_image/')),
                ('passport_image', models.ImageField(blank=True, null=True, upload_to='media/passport_image/')),
                ('user', models.ForeignKey(default=10, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
