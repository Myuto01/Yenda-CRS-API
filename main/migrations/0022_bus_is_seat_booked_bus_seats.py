# Generated by Django 4.1.3 on 2024-04-22 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_alter_ticket_passenger_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='is_seat_booked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bus',
            name='seats',
            field=models.JSONField(default=dict),
        ),
    ]
