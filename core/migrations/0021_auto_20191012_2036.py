# Generated by Django 2.2.5 on 2019-10-13 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20191009_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='gengroup',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gengroup',
            name='title',
            field=models.CharField(blank=True, max_length=500, null=True, unique=True),
        ),
    ]
