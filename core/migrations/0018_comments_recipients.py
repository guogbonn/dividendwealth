# Generated by Django 2.2.5 on 2019-10-07 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_commentreply'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='recipients',
            field=models.ManyToManyField(blank=True, related_name='recipients', to='core.User_Profile'),
        ),
    ]
