# Generated by Django 4.2.3 on 2023-08-22 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "schedule",
            "0008_rename_schedule_schedules_aircrafttype_aircraft_logo_and_more",
        ),
        ("login", "0003_alter_users_station"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="station",
            field=models.ForeignKey(
                default="",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="schedule.stations",
            ),
        ),
    ]
