# Generated by Django 3.1.7 on 2021-04-25 02:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0002_clearedlesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='clearedlesson',
            name='cleared_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
