# Generated by Django 3.1.7 on 2021-05-09 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0018_auto_20210508_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='bookmark_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
