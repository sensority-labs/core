# Generated by Django 5.1.3 on 2024-11-25 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0004_watchman"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="system_user_name",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Имя пользователя GIT"
            ),
        ),
    ]
