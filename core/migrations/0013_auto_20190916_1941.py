# Generated by Django 2.2.5 on 2019-09-17 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20190916_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinfo',
            name='date_included',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
