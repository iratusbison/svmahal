# Generated by Django 3.2.7 on 2024-02-08 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('svapp', '0005_remove_booking_checkin_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='room',
        ),
        migrations.AddField(
            model_name='booking',
            name='rooms',
            field=models.ManyToManyField(to='svapp.Room'),
        ),
    ]