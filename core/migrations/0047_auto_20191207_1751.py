# Generated by Django 2.2.5 on 2019-12-08 00:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20191207_1738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='downloadedf',
            new_name='downloaded_num',
        ),
    ]
