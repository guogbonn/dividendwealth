# Generated by Django 2.2.5 on 2020-04-03 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_auto_20200403_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='gengroup',
            name='zoom_active_meeting',
            field=models.BooleanField(default=False),
        ),
    ]
