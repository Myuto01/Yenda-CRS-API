# Generated by Django 4.1.3 on 2024-04-22 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_remove_ticket_buyer_booking_ticket_bus_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='passenger_age',
            new_name='passenger_email',
        ),
    ]