# Generated by Django 3.1.7 on 2021-06-01 11:39

import def_i.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('def_i', '0021_auto_20210518_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_image_1',
            field=models.ImageField(blank=True, null=True, upload_to='def_i/img', validators=[django.core.validators.validate_image_file_extension, def_i.validators.FileSizeValidator]),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_image_2',
            field=models.ImageField(blank=True, null=True, upload_to='def_i/img', validators=[django.core.validators.validate_image_file_extension, def_i.validators.FileSizeValidator]),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_image_1',
            field=models.ImageField(blank=True, null=True, upload_to='def_i/img', validators=[django.core.validators.validate_image_file_extension, def_i.validators.FileSizeValidator]),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_image_2',
            field=models.ImageField(blank=True, null=True, upload_to='def_i/img', validators=[django.core.validators.validate_image_file_extension]),
        ),
    ]