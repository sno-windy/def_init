# Generated by Django 3.1.7 on 2021-06-07 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0023_auto_20210605_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='for_lesson_complete',
            field=models.BooleanField(default=False),
        ),
    ]
