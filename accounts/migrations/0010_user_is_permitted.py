# Generated by Django 3.1.7 on 2021-10-13 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20210608_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_permitted',
            field=models.BooleanField(default=False),
        ),
    ]