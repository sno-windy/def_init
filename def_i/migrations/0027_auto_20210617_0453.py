# Generated by Django 3.1.7 on 2021-06-16 19:53

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0026_auto_20210617_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='msg',
            field=markdownx.models.MarkdownxField(max_length=5000),
        ),
    ]
