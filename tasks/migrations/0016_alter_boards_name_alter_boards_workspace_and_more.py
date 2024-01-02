# Generated by Django 4.1 on 2023-12-23 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_alter_card_max_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name='boards',
            name='workspace',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='card',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='card',
            name='title',
            field=models.CharField(max_length=250),
        ),
    ]