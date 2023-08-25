# Generated by Django 4.2.3 on 2023-08-22 07:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("schedule", "0007_alter_schedule_arrival_time_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Schedule",
            new_name="Schedules",
        ),
        migrations.AddField(
            model_name="aircrafttype",
            name="aircraft_logo",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="airlines",
            name="logo_image",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="stations",
            name="country",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="stations",
            name="station_logo",
            field=models.TextField(default=""),
        ),
    ]
