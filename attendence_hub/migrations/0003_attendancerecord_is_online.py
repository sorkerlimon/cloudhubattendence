# Generated by Django 5.1.1 on 2024-10-13 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendence_hub', '0002_alter_attendancerecord_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancerecord',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]
