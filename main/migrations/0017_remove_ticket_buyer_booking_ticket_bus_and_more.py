# Generated by Django 4.1.3 on 2024-04-22 04:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_driverdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='buyer_booking',
        ),
        migrations.AddField(
            model_name='ticket',
            name='bus',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main.bus'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='passenger_age',
            field=models.CharField(default='', max_length=3),
        ),
        migrations.AddField(
            model_name='ticket',
            name='seat_number',
            field=models.CharField(default='', max_length=7),
        ),
    ]
