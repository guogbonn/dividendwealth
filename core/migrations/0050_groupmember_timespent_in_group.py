# Generated by Django 2.2.5 on 2019-12-12 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20191209_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmember',
            name='timespent_in_group',
            field=models.IntegerField(default=0),
        ),
    ]
