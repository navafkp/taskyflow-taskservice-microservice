# Generated by Django 4.1 on 2023-12-13 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_alter_columns_position'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignee',
            old_name='card',
            new_name='card_id',
        ),
    ]
