# Generated by Django 3.1.7 on 2021-06-07 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20210608_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='position',
            field=models.CharField(choices=[('インターン生', 'インターン生'), ('エンジニア', 'エンジニア'), ('デザイナー', 'デザイナー'), ('凄いエンジニア', '凄いエンジニア'), ('素晴らしいデザイナー', '素晴らしいデザイナー'), ('運営', '運営')], default='intern', max_length=16),
        ),
    ]
