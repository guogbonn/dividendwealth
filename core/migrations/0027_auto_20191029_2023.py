# Generated by Django 2.2.5 on 2019-10-30 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_groupmember_member_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_img'),
        ),
    ]
