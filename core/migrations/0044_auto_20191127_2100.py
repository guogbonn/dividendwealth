# Generated by Django 2.2.5 on 2019-11-28 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20191127_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockwatchlist',
            name='added',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stockwatchlist',
            name='checked',
            field=models.BooleanField(default=True),
        ),
    ]
