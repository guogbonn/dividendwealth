# Generated by Django 2.2.5 on 2019-09-19 02:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20190916_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='gengroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='gengroup',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to='core.User_Profile'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='joined',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
