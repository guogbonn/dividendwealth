# Generated by Django 2.2.5 on 2019-12-14 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20191212_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='notification_count',
            field=models.IntegerField(default=0),
        ),
    ]
