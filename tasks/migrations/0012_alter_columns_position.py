# Generated by Django 4.1 on 2023-12-12 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_alter_columns_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='columns',
            name='position',
            field=models.CharField(default='1', max_length=50),
        ),
    ]
