# Generated by Django 4.1 on 2023-12-09 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('max_members', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('column', models.CharField(default='1', max_length=15)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.boards')),
            ],
        ),
        migrations.CreateModel(
            name='Assignee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.card')),
            ],
        ),
    ]
