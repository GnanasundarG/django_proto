# Generated by Django 4.2.3 on 2023-07-27 08:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("acl", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="api_url_access",
            name="id_api_url_access",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
