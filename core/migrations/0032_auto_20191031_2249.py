# Generated by Django 2.2.5 on 2019-11-01 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20191031_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archive',
            name='userprofile',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.User_Profile'),
        ),
    ]
