# Generated by Django 4.1 on 2023-12-28 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0022_boards_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='color',
            field=models.CharField(default='#ffffff', max_length=100),
        ),
    ]