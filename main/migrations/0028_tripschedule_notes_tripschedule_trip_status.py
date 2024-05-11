# Generated by Django 4.1.3 on 2024-05-10 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_tripschedule_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripschedule',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tripschedule',
            name='trip_status',
            field=models.CharField(blank=True, default='Upcoming', max_length=30, null=True),
        ),
    ]
