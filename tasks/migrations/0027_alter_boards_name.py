# Generated by Django 4.1 on 2024-01-02 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0026_meeting_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
