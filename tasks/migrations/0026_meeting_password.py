# Generated by Django 4.1 on 2024-01-01 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0025_meeting_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='password',
            field=models.CharField(default='67ashg', max_length=100),
        ),
    ]
