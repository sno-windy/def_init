# Generated by Django 3.1.7 on 2021-05-18 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0020_auto_20210512_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_image',
            field=models.FileField(upload_to='def_i/img'),
        ),
    ]