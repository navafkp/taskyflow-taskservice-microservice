# Generated by Django 4.1 on 2023-12-28 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0023_card_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='priority',
            field=models.CharField(default='high', max_length=30),
        ),
    ]
