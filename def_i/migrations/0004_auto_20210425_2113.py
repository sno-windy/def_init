# Generated by Django 3.1.7 on 2021-04-25 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0003_clearedlesson_cleared_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='has_noticed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='talk',
            name='has_noticed',
            field=models.BooleanField(default=False),
        ),
    ]
