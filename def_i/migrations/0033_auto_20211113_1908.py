# Generated by Django 3.1.7 on 2021-11-13 10:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0032_auto_20211103_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='clearedlesson',
            name='cleared_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 13, 10, 8, 57, 275303, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]