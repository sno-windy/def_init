# Generated by Django 3.1.7 on 2021-05-04 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('def_i', '0010_auto_20210503_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=10)),
                ('category_image', imagekit.models.fields.ProcessedImageField(blank=True, upload_to='def_i/img')),
                ('description', models.TextField(max_length=100, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='course',
            name='course_category',
        ),
        migrations.RemoveField(
            model_name='studyingcategory',
            name='course_category',
        ),
        migrations.AlterField(
            model_name='studyingcategory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_category', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='def_i.category'),
        ),
        migrations.AddField(
            model_name='studyingcategory',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='studying_category', to='def_i.category'),
            preserve_default=False,
        ),
    ]